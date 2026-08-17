# Vitality Check-in — offline-first prototype

Replaces the Power Apps hospitality-suite check-in tool with something that
keeps working when there's no signal at the venue.

## How it works
- **Load member list (Excel)** — import the latest Team Vitality export. The
  app asks (once per file) which columns hold the ID number, name, and tier,
  since the exact export headers aren't fixed. The list is cached in a local
  SQLite database at `~/.vitality_checkin/local.db`.
- **Verify** — type or scan an ID number and press Enter. Lookup is instant
  and needs no connection, because it's checked against the local cache, not
  a live server.
- Every check (granted or denied) is logged locally and shown in the recent
  check-ins table.
- **Export check-in log** — save the day's log to Excel, for reporting or to
  hand back to Discovery.
- **Sync now** — currently a placeholder. Once there's an approved API or
  database endpoint, this button is where periodic pulling of a fresh member
  list and pushing of the check-in log would go — automatically, whenever a
  connection is available, with no interruption if it isn't.

## Running it
```bash
pip install -r requirements.txt
python app/main.py
```

## Running it in GitHub Codespaces
This repo includes a `.devcontainer` config, so Codespaces gets a working
Python + Qt setup automatically — including a virtual desktop, since a
PySide6 window needs somewhere to actually display in a browser-only
environment.

1. Push this project to a GitHub repo.
2. On the repo page: **Code → Codespaces → Create codespace on main**.
3. Wait for the container to build (installs Python deps + desktop support
   automatically via `postCreateCommand`).
4. Open the **Ports** tab, find port `6080` ("Desktop (noVNC)"), and open it
   in the browser — that's your virtual desktop.
5. In the Codespace terminal, run `python app/main.py`. The app window
   appears inside that virtual desktop tab.
6. Commit and push as normal — this is just a regular git repo underneath.

## Packaging as a standalone .exe (for a laptop with no Python installed)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VitalityCheckin app/main.py
```
The output lands in `dist/VitalityCheckin.exe`. Copy that one file to any
Windows machine and double-click to run — nothing else needs installing.

## Handling real member data
ID numbers are sensitive personal information. Keep the imported Excel file
and the local `.vitality_checkin` folder off personal cloud storage (e.g. no
personal Dropbox/Google Drive sync), and don't commit real data to any public
repository. Check with your manager/IT on where the device and files should
live for a live event.

## What's next (v2, needs manager/IT sign-off)
- A real sync endpoint (API or shared database) so the member list refreshes
  automatically and check-in logs push up without manual export.
- Multi-device support if more than one promoter is checking IDs at once.
