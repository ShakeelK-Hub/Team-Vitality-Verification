<div align="center">

# Vitality Check-in

### Offline-first hospitality member verification

Fast, reliable member verification designed for environments where connectivity cannot be guaranteed.

**Python · PySide6 · SQLite · Pandas · OpenPyXL**

</div>

---

## Overview

**Vitality Check-in** is a desktop verification application built around a simple operational requirement: member access should not stop because venue connectivity does.

The application imports a member list from Excel, stores operational data locally in SQLite, verifies identification numbers against that local cache, records every verification attempt, and exports check-in activity for reporting.

**Import → Verify → Decide → Record → Export**

> **Project status:** Functional offline-first prototype. Production deployment, live member data, central synchronisation, or organisational integrations require the appropriate technical and operational approval.

## Why offline-first?

Hospitality check-in is an operational workflow where reliability matters more than connectivity. Requiring a live server for every lookup introduces an avoidable failure point. This project keeps the verification path local so a temporary loss of signal does not prevent an operator from checking a member.

| Principle | Implementation |
|---|---|
| **Availability** | Verification runs against a local SQLite cache. |
| **Speed** | Local lookups avoid network round trips. |
| **Simplicity** | Identify → verify → record. |
| **Auditability** | Granted and denied attempts are logged locally. |
| **Privacy** | Real member data is not included in the public repository. |
| **Extensibility** | Synchronisation can be added around the local workflow. |

## Core capabilities

**Member data**
- Import member records from Excel.
- Map ID and name columns from varying export formats.
- Cache the approved member list locally in SQLite.

**Verification**
- Enter or scan an identification number.
- Perform an immediate local lookup.
- Clearly communicate granted or denied access.
- Display relevant member information after successful verification.

**Check-in operations**
- Record every verification attempt.
- Display recent activity in the application.
- Export check-in activity to Excel for reporting.

**Development**
- Run locally with Python.
- Develop through GitHub Codespaces.
- Package as a standalone Windows executable with PyInstaller.

## Architecture

```text
                         MEMBER EXPORT
                              │
                              ▼
                     ┌─────────────────┐
                     │  Excel Import   │
                     │  + Column Map   │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Local SQLite  │
                     │      Cache      │
                     └────────┬────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Verification Flow │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               ┌─────────┐         ┌─────────┐
               │ GRANTED │         │  DENIED │
               └────┬────┘         └────┬────┘
                    │                   │
                    └─────────┬─────────┘
                              ▼
                     ┌─────────────────┐
                     │  Check-in Log   │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  Excel Export   │
                     └─────────────────┘
```

The current verification path is completely local. The **Sync now** workflow is an intentional extension point for a future approved API or database integration.

More detail: [`docs/architecture.md`](docs/architecture.md)

## Technology

| Layer | Technology |
|---|---|
| UI | PySide6 / Qt |
| Language | Python |
| Persistence | SQLite |
| Spreadsheet processing | Pandas / OpenPyXL |
| Development | Git / GitHub Codespaces |
| Packaging | PyInstaller |
| Automation | GitHub Actions |

## Project structure

```text
Team-Vitality-Verification/
├── app/
│   ├── main.py             # Application UI and workflow
│   ├── db.py               # SQLite persistence and logging
│   └── excel_import.py     # Excel import and column mapping
├── docs/
│   ├── architecture.md    # System design and data flow
│   ├── deployment.md      # Local, Codespaces and Windows deployment
│   ├── security.md        # Security and privacy guidance
│   └── contributing.md    # Contribution guidelines
├── .github/
│   ├── ISSUE_TEMPLATE/     # Standardised issue reporting
│   └── workflows/          # Automated validation
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting started

### Requirements

- Python 3.10+
- pip
- Windows, macOS or Linux for development

### Install

```bash
git clone https://github.com/ShakeelK-Hub/Team-Vitality-Verification.git
cd Team-Vitality-Verification
pip install -r requirements.txt
```

### Run

```bash
python app/main.py
```

The local operational database is created under:

```text
~/.vitality_checkin/local.db
```

Use synthetic data for development and demonstrations.

## GitHub Codespaces

The project is designed for Codespaces development. Because PySide6 is a desktop GUI framework, browser-based development requires a virtual desktop environment when running the application remotely.

1. Open the repository in Codespaces.
2. Allow the development environment to initialise.
3. Install dependencies if required.
4. Run `python app/main.py`.
5. Open the configured virtual desktop port when using a browser-only environment.

See [`docs/deployment.md`](docs/deployment.md).

## Windows executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VitalityCheckin app/main.py
```

Output:

```text
dist/VitalityCheckin.exe
```

## Data, privacy and security

Identification numbers and member information can constitute sensitive personal information. This public repository contains **code and synthetic/demo concepts only** and must never contain real member exports.

For real deployments:

- Never commit member exports, local databases or generated reports.
- Keep operational data outside the Git repository.
- Use an organisation-approved device and storage location.
- Apply appropriate access controls.
- Follow applicable data-retention and privacy requirements.
- Obtain approval before connecting organisational systems.

Read [`docs/security.md`](docs/security.md).

## Roadmap

### Completed

- [x] Offline member verification
- [x] Local SQLite member cache
- [x] Excel member import
- [x] ID / name mapping
- [x] Granted and denied states
- [x] Local check-in logging
- [x] Excel check-in export
- [x] Codespaces development support

### Planned

- [ ] Automated member synchronisation
- [ ] Centralised check-in synchronisation
- [ ] Multi-device operation
- [ ] Role-based operator access
- [ ] Expanded automated test coverage
- [ ] Production deployment architecture
- [ ] Operational analytics and reporting

## Engineering notes

The project deliberately separates current functionality from future product direction. It does not claim to provide live synchronisation, production identity verification, or an official connection to organisational systems.

The local verification workflow is implemented today; central synchronisation is an architectural extension point for a future approved environment.

## Contributing

This repository is primarily a portfolio and prototype project. Contributions should preserve the offline-first design, avoid real personal data, and include appropriate documentation for meaningful behavioural changes.

See [`docs/contributing.md`](docs/contributing.md).

## License

No open-source licence is currently granted. All rights remain with the repository owner unless otherwise stated.

---

<div align="center">

**Vitality Check-in**  
Offline-first verification for reliable hospitality operations.

</div>
