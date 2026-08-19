# Deployment Guide

## Local development

Install Python 3.10 or newer, then:

```bash
git clone https://github.com/ShakeelK-Hub/Team-Vitality-Verification.git
cd Team-Vitality-Verification
pip install -r requirements.txt
python app/main.py
```

## GitHub Codespaces

The repository includes a development-container configuration for browser-based development.

1. Create a Codespace from the `main` branch.
2. Wait for the development container to finish initialisation.
3. Run `python app/main.py`.
4. When using a browser-only environment, open the configured virtual desktop port.

PySide6 requires a display server. Codespaces therefore needs the project's virtual desktop setup rather than a normal terminal-only execution environment.

## Windows packaging

For a standalone demonstration build:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VitalityCheckin app/main.py
```

The executable is created in `dist/VitalityCheckin.exe`.

## Production considerations

A production deployment should not be treated as a simple executable copy. Before using real member information, establish:

- approved device and storage controls;
- access permissions;
- data-retention requirements;
- backup and recovery procedures;
- approved synchronisation architecture;
- logging and audit requirements;
- application update and distribution controls.

Production deployment requires the relevant organisational approval.
