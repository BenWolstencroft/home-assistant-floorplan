# Contributing to Floorplan Integration

We welcome contributions! This document describes how to develop and submit changes.

## Development Setup

### Prerequisites

- Python 3.11+
- Home Assistant development environment
- Git

### Setup Steps

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/home-assistant-floorplan.git
   cd home-assistant-floorplan
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Development Workflow

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes in `custom_components/floorplan/`

3. Check your work:
   ```bash
   python -m pylint custom_components/floorplan/
   python -m black --check custom_components/floorplan/
   python -m isort --check-only custom_components/floorplan/
   python -m mypy custom_components/floorplan/
   ```

4. Run tests:
   ```bash
   python -m pytest tests/
   ```

5. Commit with clear messages:
   ```bash
   git commit -m "feat: add feature description"
   ```

### Code Style

- **Python**: Follow PEP 8
- **Type hints**: Add type annotations to all functions
- **Docstrings**: Include docstrings for classes and public methods
- **Formatting**: Use `black` for code formatting
- **Imports**: Organize with `isort`

## Testing

### Running Tests

```bash
python -m pytest tests/ -v
```

### Writing Tests

- Add tests to `tests/` directory
- Follow pytest conventions
- Test both success and error cases
- Include type hints in test functions

## Pull Request Process

1. **Update documentation**: If adding features, update README.md
2. **Update changelog**: Add your changes to CHANGELOG.md under [Unreleased]
3. **Pass validation**: Ensure GitHub Actions workflows pass:
   - HACS validation
   - Hassfest validation
   - Black formatting
   - isort import sorting
   - Flake8 linting
   - mypy type checking
4. **Add tests**: Include tests for new functionality
5. **Request review**: Submit your PR with a clear description

## CI/CD Pipeline

The project uses GitHub Actions for automated validation:

### Validate Workflow (`validate.yml`)
Runs on every push to main/develop and PRs:
- **HACS validation**: Checks HACS requirements
- **Hassfest validation**: Validates Home Assistant component
- **Linting**: Black, isort, flake8
- **Type checking**: mypy static analysis
- **Tests**: pytest test suite

### Release Workflow (`release.yml`)
Triggered by tags like `v1.0.0`:
- Validates the release
- Updates version in manifest.json
- Creates a GitHub release

## Home Assistant Integration Testing

1. Copy the component to your Home Assistant:
   ```bash
   cp -r custom_components/floorplan ~/.homeassistant/custom_components/
   ```

2. Restart Home Assistant

3. Add the integration:
   - Go to **Settings → Devices & Services → Create Integration**
   - Search for "Floorplan"
   - Configure as needed

## Code Structure

```
custom_components/floorplan/
├── __init__.py              # Integration setup, services
├── config_flow.py           # Configuration UI
├── const.py                 # Constants and configuration keys
├── floorplan_manager.py     # Data management
├── location_provider.py     # Location provider interface
├── entity.py                # Custom entities
├── manifest.json            # Integration metadata
├── providers/               # Location providers
│   ├── __init__.py
│   └── bermuda.py          # Bermuda trilateration provider
└── translations/            # i18n translations
    └── en.json
```

## Commit Message Conventions

Use conventional commits:

```
feat: add new feature
fix: fix a bug
docs: update documentation
refactor: code restructuring
test: add/update tests
chore: maintenance tasks
```

Example:
```
feat: add ESPresense location provider

- Implement ESPresense provider interface
- Add distance sensor discovery
- Include trilateration algorithm
- Add comprehensive documentation
```

## Code of Conduct

Please be respectful and constructive in all interactions within this project.

## Contributor License Agreement

By submitting code to this project, you agree that your work may be used under the terms of this project's license.

## Questions or Issues?

- Open an issue on GitHub
- Check existing issues for similar problems
- Review the README.md and documentation

Thank you for contributing to the Floorplan project!
