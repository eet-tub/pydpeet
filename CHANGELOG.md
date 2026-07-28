# 0.4.1

Contributions from:
- Daniel Schröder (daniel_shr)

Bugfixes:
- updated API to use correct function name extract_instructions
- loosened up dependencies too major version (e.g. 3.X.Y) if dependency is over version 1.0 to increase compatibility

Tasks:
- updated CI to check if project is installable on python 3.12-3.14
- updated CI to check test coverage (now fails on missing tests for a variable, duplicates, deprecations)

# 0.4.0

Contributions from:
- Martin Otto (MAtahualpa)
- Anton Schlösser (schlanto)
- Daniel Schröder (daniel_shr)
- Max Thorn (northmaybe)

Features:
- Made different types of config more consistent
- Step Analyzer: Unified config for all functions

Bugfixes:
- Digatron (v4.20.6.236): Fix infinite loop in reader
- Digatron EIS meter (v4.20.6.236): Fix infinite loop in reader
- Added 'calamine' as default Excel reading engine in all places

Tasks:
- Migrated from GitLab (TU Berlin) to GitHub
- Filled in 'AUTHORS.md', 'CHANGELOG.md', and 'CONTRIBUTING.md' [[#6](https://github.com/eet-tub/pydpeet/issues/6)]
- Set up GitHub workflows after migrating from GitLab (TU Berlin) [[#7](https://github.com/eet-tub/pydpeet/issues/7), [#9](https://github.com/eet-tub/pydpeet/issues/9), [#10](https://github.com/eet-tub/pydpeet/issues/10), [#11](https://github.com/eet-tub/pydpeet/issues/11)]
- Added badges to 'README.md' [[#13](https://github.com/eet-tub/pydpeet/issues/13)]
- Added version switch to GitHub Pages website [[#14](https://github.com/eet-tub/pydpeet/issues/14)]
- Added new iteration of example notebooks
- Added support for new 'pandas' main version and bumped dependency to version 3.0.3
- Added recent PyDPEET-related publications

# 0.3.1

This release was published while the project was still hosted on GitLab (TU Berlin) and mirrored to GitHub

Contributions from:
- Anton Schlösser (schlanto)
- Daniel Schröder (daniel_shr)
- Max Thorn (northmaybe)

Bugfixes:
- Digatron (v4.20.6.236): Fixed file encoding (is "iso-8859-1" now)
- Digatron (v4.20.6.236): Fixed errors in reader

Tasks:
- Fixed authors for PyPI release page

# 0.3.0

This release was published while the project was still hosted on GitLab (TU Berlin) and mirrored to GitHub

Contributions from:
- Martin Otto (MAtahualpa)
- Anton Schlösser (schlanto)
- Daniel Schröder (daniel_shr)
- Max Thorn (northmaybe)

Bugfixes:
- Neware (v8.0.0.516): Fixed error when searching for main file
- Parstat (v2.63.3): Fixed infinite loops in reader

Tasks:
- Added basic test coverage
- Improved example notebooks
- Improved 'README.md' and GitHub Pages

# 0.2.0

This release was published while the project was still hosted on GitLab (TU Berlin) and mirrored to GitHub

Contributions from:
- Cataldo De Simone
- Alexander Hinrichsen
- Jan Kalisch
- Martin Otto (MAtahualpa)
- Anton Schlösser (schlanto)
- Daniel Schröder (daniel_shr)

Features:
- Supported cyclers:
    - Arbin (v4.23)
    - Arbin (v8.00)
    - BaSyTec (v6.3.1.0)
    - Digatron (v4.20.6.236)
    - Neware (v8.0.0.516)
    - Parstat (2.63.3)
    - Safion (v1.9)
- Provided functions:
    - 'read', 'convert', 'write'
    - merge tests of single cell (test series), merge test series of multiple cells (test campaign)
    - sequence analyzer: identify, extract, and visualise patterns in measurement data according to a set of rules (default or custom)
    - basic analysis functionality: cycles, charge throughput, capacity, power, energy, resistance, SOC, SOH, efficiency

Tasks:
- Initial public release using official version number
- First PyPI release
- Set up GitLab pipeline and first iteration of GitHub Pages
- Added first iteration of example notebooks