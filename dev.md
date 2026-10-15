# Court Automation — developer notes

Version 0.3.0 targets CK3 1.20.1.1. This repository is a portable, reviewed publication projection. Runtime files are at the repository root; canonical player copy is [publishing/description.en.md](publishing/description.en.md). Regenerate README with `python tools/render_readme.py`.

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

## 0.2.2 notification context correction

Court Init and Bare Knights now pass their result message through the native `custom_tooltip` toast field. Both decisions save the recipient as `ca_result_recipient`; their two result descriptions use that named scope in every supported language. This changes delivery and counter resolution, without changing appointment selection, recruitment, salaries, AI budgets or scheduling.

The two descriptions retain the same wording in all nine languages. The other 47 localization values in each language and all unaffected runtime files retain the prior bytes. Unchanged literal and gameplay evidence may be inherited only through its recorded exact-source scope. Candidate-specific notification, salary and physician content evidence and the complete localization acceptance are maintained in release verification records. This portable source copy itself is not a native acceptance receipt; visual coverage remains separate.

## CAA family metadata revision

The current publication copy includes all seven other maintained mods, with Steam Workshop links. Update only the canonical My other mods block and project that block into the existing README and platform outputs; preserve the rest of each platform description. Parley and Vassalization Extended Steam exports use whitespace-only BBCode compaction to remain within the 8,000-byte UTF-8 CRLF form limit. Recheck the current shared publication contract and scoped release metadata guide before publishing. Runtime, version, archives, media, and prior localization evidence are unchanged.

## Release 0.3.0 — CK3 1.20.1

Updated for CK3 1.20.1. Add continuous court and knight staffing, knight filter reset/locking, and Court Jester exclusion. Preserve automation preferences and saved court policies through succession. Label the four native-policy buttons and update bodyguard prestige salary estimates.

The committed runtime is the current release source. Earlier generator/test notes above retain their historical scope. Gameplay evidence is inherited from the reviewed development candidate; localization uses static coverage and format checks under publication contract 1.8.0. No additional production engine run or blanket multiplayer/visual guarantee is claimed.

## Compatibility metadata — CK3 1.20.1.1 (2026-10-15)

Version 0.3.0 now targets CK3 1.20.1.1 (Steam build 25913294). This is a publication metadata update; runtime files, mod version, release history and existing download archives are unchanged.

The upstream comparison used the complete Steam manifests for 1.20.1 and 1.20.1.1 and verified the installed main game, Windows and launcher files against the current manifests. All main-game GUI files and gameplay scripts used by this mod retain their upstream hashes; changes are concentrated in translations, name equivalency and French customizable localization. The executable changed. Mod-specific source and localization checks are recorded in the maintained compatibility assessment and release journal.

Earlier native reports retain their original source, game build and scenario coverage. This metadata revision does not claim a fresh native PASS on 1.20.1.1. Visual layout, multiplayer and performance retain their previously recorded limits. Edit the canonical publication source and regenerate its current outputs; preserve historical release records.
