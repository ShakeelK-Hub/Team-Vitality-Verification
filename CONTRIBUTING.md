# Contributing

## Development principles

Contributions should keep the project focused on reliable, simple and privacy-conscious member verification.

### Before changing code

- Understand the existing verification flow.
- Keep real member data out of the repository.
- Prefer small, focused changes.
- Update documentation when behaviour or setup changes.

### Pull requests

A useful pull request should explain:

1. what changed;
2. why the change was needed;
3. how it was tested;
4. whether documentation was updated;
5. whether the change affects data handling or security.

### Commit messages

Use clear, action-oriented messages such as:

```text
feat: improve verification workflow
docs: document Codespaces setup
fix: handle malformed member exports
test: add database verification coverage
```

### Data policy

Never use real member records in tests, screenshots, examples or commits. Use synthetic data instead.
