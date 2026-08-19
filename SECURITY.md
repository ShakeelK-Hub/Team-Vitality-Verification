# Security and Privacy

## Scope

Vitality Check-in can process identification numbers, names and membership tiers. These fields may constitute personal or sensitive information depending on the deployment context.

## Public repository policy

This repository must contain source code and synthetic demonstration data only.

Do not commit:

- real member spreadsheets;
- real identification numbers;
- local SQLite databases;
- exported check-in reports;
- credentials, API keys or tokens;
- production configuration containing private endpoints.

## Local data

The application stores its local database under the user's home directory in `.vitality_checkin`. Operational data should remain outside source control and should be protected by the controls of the approved device.

## Production use

Before processing real member information, confirm the approved deployment location, access controls, retention period, backup strategy and integration architecture with the relevant technical and operational stakeholders.

## Future integrations

Any central API or database integration should use authenticated transport, least-privilege access, controlled secrets, appropriate logging and explicit failure handling. Synchronisation must not make the core check-in experience fail solely because connectivity is unavailable.

## Reporting a vulnerability

Do not publish sensitive security details, credentials or personal information in a public issue. Contact the repository owner privately through an appropriate GitHub communication channel with enough information to reproduce the issue safely.
