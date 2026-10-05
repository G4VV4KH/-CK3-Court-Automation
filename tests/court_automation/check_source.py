"""Read-only integration checks for Court Automation's source package.

Run with Python 3: check_source.py --game-root PATH_TO_CK3_GAME
This complements native probes; it does not claim to validate engine behavior.
"""

from __future__ import annotations

import argparse
import codecs
from collections import Counter
import hashlib
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT
RUNTIME_DIRS = {"common", "gui", "localization", "events"}
LANGUAGES = ("english", "french", "german", "japanese", "korean", "polish", "russian", "simp_chinese", "spanish")
REVIEWED_OVERRIDES = {
    "gui/window_court.gui": "e730078c5f671e7e564c6e7799215d9fabda0546d38ba615f26302b122ad5135",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def without_comments(text: str, source: Path) -> str:
    """Keep quoted text intact, reject unclosed strings, and strip # comments."""
    result = []
    quoted = escaped = comment = False
    for char in text:
        if comment:
            if char == "\n":
                comment = False
                result.append(char)
        elif quoted:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == "#":
            comment = True
        else:
            result.append(char)
            quoted = char == '"'
    require(not quoted, f"Unclosed quoted string: {source}")
    return "".join(result)


def check_braces(text: str, source: Path) -> str:
    clean = without_comments(text, source)
    unquoted = re.sub(r'"(?:[^"\\]|\\.)*"', '""', clean, flags=re.S)
    depth = 0
    for char in unquoted:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            require(depth >= 0, f"Unexpected closing brace: {source}")
    require(depth == 0, f"Unclosed brace: {source}")
    return clean


def read_bom(path: Path) -> str:
    data = path.read_bytes()
    require(data.startswith(codecs.BOM_UTF8), f"Missing UTF-8 BOM: {path}")
    return data.decode("utf-8-sig")


def read_localization(language: str) -> dict[str, str]:
    keys: dict[str, str] = {}
    files = sorted((MOD / "localization" / language).glob("*.yml"))
    require(bool(files), f"No {language} localization files")
    entry = re.compile(r'\s*([A-Za-z0-9_.-]+):\d+\s+"((?:[^"\\]|\\["\\nrt])*)"\s*')
    for path in files:
        lines = without_comments(read_bom(path), path).splitlines()
        meaningful = [(n, line) for n, line in enumerate(lines, 1) if line.strip()]
        require(bool(meaningful) and meaningful[0][1].strip() == f"l_{language}:", f"Wrong localization header: {path}")
        for number, line in meaningful[1:]:
            match = entry.fullmatch(line)
            require(match is not None, f"Invalid quoted localization or escape: {path}:{number}")
            assert match is not None
            key, value = match.groups()
            require(key not in keys, f"Duplicate {language} localization key: {key}")
            keys[key] = value
    return keys


def check(game: Path) -> None:
    require((game / "common" / "court_positions" / "types").is_dir(), f"Not a CK3 game directory: {game}")
    unexpected = {p.name for p in MOD.iterdir() if p.is_dir()} - RUNTIME_DIRS - {"publishing", "tools", "tests", "docs", ".git"}
    require(not unexpected, f"Unexpected top-level mod folders: {sorted(unexpected)}")
    files = sorted(p for p in MOD.rglob("*") if p.is_file() and p.relative_to(MOD).parts[0] in RUNTIME_DIRS)
    require(bool(files), "No runtime files found")
    collisions = [p.relative_to(MOD).as_posix() for p in files if (game / p.relative_to(MOD)).exists()]
    require(not set(collisions) - REVIEWED_OVERRIDES.keys(), f"Unreviewed vanilla overrides: {collisions}")
    for relative in collisions:
        vanilla = game / relative
        require(hashlib.sha256(vanilla.read_bytes()).hexdigest() == REVIEWED_OVERRIDES[relative],
                f"Vanilla changed; review and rebase the court panel insertion: {relative}")
        edited = (MOD / relative).read_text(encoding="utf-8-sig")
        stripped, count = re.subn(r"^[\t ]*# CA_COURT_PANEL_BEGIN\n.*?^[\t ]*# CA_COURT_PANEL_END\n", "", edited, flags=re.M | re.S)
        require(count == 1 and stripped == vanilla.read_text(encoding="utf-8-sig"),
                f"Override differs outside the reviewed insertion: {relative}")

    texts: dict[Path, str] = {}
    for path in files:
        if path.suffix in {".txt", ".gui"}:
            texts[path] = check_braces(read_bom(path), path)
    descriptor = MOD / "descriptor.mod"
    texts[descriptor] = check_braces(descriptor.read_text(encoding="utf-8-sig"), descriptor)
    for path, text in texts.items():
        require(not re.search(r"\breplace_path\s*=", text), f"replace_path is forbidden: {path}")

    languages = {p.name for p in (MOD / "localization").iterdir() if p.is_dir()}
    native_languages = set(re.findall(r"^l_([a-z_]+):\s*$", (game / "localization/languages.yml").read_text(encoding="utf-8-sig"), re.M))
    require(native_languages == set(LANGUAGES), f"Review changed native language set: {sorted(native_languages)}")
    require(languages == native_languages, f"Localization languages differ from CK3: {sorted(languages)}")
    localized = {language: read_localization(language) for language in LANGUAGES}
    english = localized["english"]
    tokens = re.compile(r"\[[^\]\r\n]*\]|\$[^$\r\n]+\$|@[A-Za-z0-9_]+!|#[A-Za-z][A-Za-z0-9_:.-]*|#!|\\n")
    for language, strings in localized.items():
        require(english.keys() == strings.keys(), f"{language} localization key mismatch: missing={sorted(english.keys() - strings.keys())}, extra={sorted(strings.keys() - english.keys())}")
        for key, value in strings.items():
            require(bool(value.strip()), f"Empty localization: {language}/{key}")
            require(Counter(tokens.findall(value)) == Counter(tokens.findall(english[key])),
                    f"Changed script/icon/formatting/newline tokens: {language}/{key}")
            require(not any(ord(c) < 32 and c not in "\t\n\r" for c in value), f"Control character in {language}/{key}")

    references: set[str] = set()
    direct = re.compile(r'\b(?:text|tooltip|desc|title|custom_tooltip|confirm_text)\s*=\s*"?(ca_\w+)\b')
    for path, text in texts.items():
        references.update(direct.findall(text))
        references.update(re.findall(r"\bLocalize\(\s*['\"](ca_\w+)['\"]", text))
        if path.parent.name == "decisions":
            for key in re.findall(r"^(ca_\w+)\s*=\s*\{", text, re.M):
                references.update(key + suffix for suffix in ("", "_desc", "_tooltip", "_confirm"))
        references.update("decision_group_type_" + key for key in re.findall(r"\bdecision_group_type\s*=\s*(ca_\w+)", text))
    for value in (value for strings in localized.values() for value in strings.values()):
        references.update(re.findall(r"\$(ca_\w+)(?:\|[^$]*)?\$", value))
        references.update(re.findall(r"\bLocalize\(\s*['\"](ca_\w+)['\"]", value))
    require(not references - english.keys(), f"Unresolved localization references: {sorted(references - english.keys())}")
    require(
        (MOD / "README.md").read_text(encoding="utf-8-sig") == (MOD / "publishing" / "description.en.md").read_text(encoding="utf-8-sig"),
        "README differs from canonical publishing/description.en.md",
    )

    for generator in ("build_court_roles.py", "build_court_salaries.py", "build_court_ai.py"):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / generator), "--game-root", str(game), "--check"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        require(completed.returncode == 0, f"Generator drift check failed ({generator}):\n" + completed.stdout + completed.stderr)
        print(completed.stdout.strip())
    print(f"PASS: {len(texts) - 1} BOM script files; balanced scripts/descriptor; {len(english)} matching keys in all {len(localized)} native languages; script/icon/formatting tokens preserved; {len(references)} resolved localization references.")
    print(f"PASS: {len(files)} runtime files; {len(collisions)} reviewed minimal vanilla overrides; approved folders; no replace_path; canonical README matches.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        check(args.game_root)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
