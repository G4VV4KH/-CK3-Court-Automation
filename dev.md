# Court Automation — developer notes

Version 0.2.1 targets CK3 1.20.0.3. This repository is a portable, reviewed publication projection. Runtime files are at the repository root; canonical player copy is [publishing/description.en.md](publishing/description.en.md). Regenerate README with `python tools/render_readme.py`.

## Implementation

- Court automation uses native court-position commands across all position types. Four policies apply when positions become vacant. It does not continuously replace incumbents.
- Court Init covers 53 non-camp position types and 59 defined slots. It fills available vacancies in a stable order, choosing the highest eligible aptitude for each slot; it is not a global optimization. Existing holders and councillors remain. New courtiers have random skills with only mandatory qualifications ensured. Favored Minister still needs an actual councillor; Garuda still needs a knight.
- Bare Knights fills the initial actual roster deficit with eligible random courtiers, forces their knight preference, and stops if an unexpected assignment fails. Random prowess is retained except mandatory cultural minima.
- Salary adapters reproduce native base salary formulas for gold, treasury, prestige and piety (zero where absent). Paid position tasks are excluded. Appointment-specific terms can change the estimate.
- Optional conservative AI support runs yearly for adult landed AI rulers of count rank or higher. It checks solvency, cash reserves, vanilla position priorities and buffered salaries. It creates at most two missing knights and one eligible court candidate per pass. Existing valid court candidates suppress recruitment; native AI makes the eventual appointment. The disabled rule stops this support.
- The only vanilla file replacement is `gui/window_court.gui`, with one marked insertion for the foldout. Other court-window replacements need a compatibility patch to retain both interfaces; load order alone cannot combine them.

## Checks

Run `python -B tests/court_automation/check_source.py --game-root <CK3-game-directory>` against an installed CK3 copy. It checks the reviewed vanilla window hash and exact insertion, script structure, all nine native language sets, 49 localization keys per language, technical tokens, README parity and the three generators.

The generator commands `tools/build_court_roles.py`, `tools/build_court_salaries.py` and `tools/build_court_ai.py` each take `--game-root <CK3-game-directory> --check`. After a game update, inspect changed position requirements, slot limits, salaries, AI priorities, knight eligibility and the court window before regenerating. Static checks do not establish engine compatibility.

## Verification history and limits

The final 0.2.0 native snapshot passed 51 targeted gameplay assertions (18 core, 20 salary and 13 AI) plus 17 GUI assertions including all 16 policy transitions. Manual salary observations in the HRE and Byzantium agreed with the native court panel in those scenarios. The whole CK3 log was not clean; unrelated base-game messages were present. This is scoped evidence, not an all-government, all-culture or all-DLC guarantee.

0.2.1 adds seven translations to unchanged EN/RU. Its 23 gameplay files are byte-identical to that tested 0.2.0 snapshot. All nine languages passed static key/token/BOM checks; the new translations received a separate semantic review. All-language visual review and native-speaker editing have not been completed.

The author supplied the four English gameplay screenshots in the gallery from GAME-PROD and authorized publication. They show the court tools group, a selected automation policy, Court Init's salary forecast and the Bare Knights description. No separate save/reload, succession or long-term native AI hiring result was explicitly reported. The release presentation revision adds a thumbnail and its descriptor reference; gameplay remains identical to the user's smoke candidate. Private raw logs, local test profiles and absolute machine paths are intentionally excluded from this portable export; original evidence remains archived in the maintainer's release records.

## Media and provenance

The four gallery images are authentic user-supplied screenshots. Cover artwork was generated with AI using a supplied CK3 court-icon reference, then exported to platform dimensions. [Media provenance](publishing/media/media-provenance.json) records hashes and transformations; original masters and the raw reference are retained in the maintainer's release evidence, outside runtime. Mod-specific code, interface additions, translations and publication text were generated with AI. Court-window integration adapts CK3 interface definitions by Paradox Interactive. No additional third-party license or reuse permission is granted by this record.
