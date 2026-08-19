# Architecture

## Purpose

Vitality Check-in is designed around an offline-first verification path. The operator should be able to verify a member even when venue connectivity is unavailable.

## Data flow

```text
Excel member export
        │
        ▼
Excel import + column mapping
        │
        ▼
Local SQLite member cache
        │
        ▼
Identification lookup
        │
        ├── Match ──> Granted ──┐
        │                       │
        └── No match -> Denied ─┤
                                ▼
                         Local check-in log
                                │
                                ▼
                           Excel export
```

## Components

### `app/main.py`

Owns the desktop interface and coordinates the verification workflow. The UI is intentionally simple: import the member list, enter or scan an ID, review the result, and inspect recent activity.

### `app/db.py`

Provides the local SQLite persistence layer used for the member cache and check-in records. Keeping this data local removes a network dependency from the critical verification path.

### `app/excel_import.py`

Handles spreadsheet ingestion and mapping of the required member fields. The importer does not assume that every operational export uses identical column names.

## Offline-first decision

The project treats connectivity as an enhancement rather than a prerequisite for verification.

A future synchronisation service can sit around the local workflow:

```text
                 ┌───────────────┐
                 │ Approved API  │
                 └───────┬───────┘
                         │
                  Synchronisation
                    when online
                         │
                         ▼
                ┌─────────────────┐
                │ Local SQLite DB │
                └────────┬────────┘
                         │
                         ▼
                  Local verification
```

The current **Sync now** control is therefore an extension point, not a claim that a production synchronisation service already exists.

## Data boundaries

The public repository contains source code only. Real member exports, local databases and generated check-in reports belong outside source control.

## Future architecture

Potential production extensions include:

- authenticated member-list synchronisation;
- centralised check-in event ingestion;
- conflict handling between multiple devices;
- role-based operator access;
- audit and retention controls;
- operational analytics.

These features require technical, security and operational approval before implementation against real organisational systems.
