# Contributing to Skribble SDK

Thank you for your interest in contributing to Skribble SDK! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- Report bugs and issues
- Suggest new features or improvements
- Submit pull requests
- Improve documentation
- Share feedback

## 🚀 Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/LeEricCH/skribble-sdk.git
   cd skribble-sdk
   ```

2. **Install Dependencies**
   ```bash
   pnpm install
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature
   # or
   git checkout -b fix/your-bugfix
   ```

## 💻 Development Workflow

1. **Generate Models**
   ```bash
   pnpm generate-models
   ```
   This command generates TypeScript and Python models from the schema definitions.

2. **Run Tests**
   ```bash
   pnpm test
   ```
   Ensure all tests pass before submitting your changes.

3. **Build Documentation**
   ```bash
   pnpm docs:dev
   ```
   Preview documentation changes locally.

## 📝 Pull Request Guidelines

1. **Branch Naming**
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation changes
   - `refactor/` - Code refactoring

2. **Commit Messages**
   - Use clear, descriptive commit messages
   - Start with a verb (add, fix, update, etc.)
   - Reference issues when applicable

3. **Before Submitting**
   - Update documentation if needed
   - Add tests for new features
   - Run tests locally
   - Update examples if applicable
   - Regenerate models if schema changed

4. **Pull Request Description**
   - Clearly describe the changes
   - Link related issues
   - Include screenshots for UI changes
   - List breaking changes if any

## 🏗️ Project Structure

```
skribble-sdk/
├── docs/            # Documentation
├── examples/        # Example projects
├── packages/        # Shared utilities and configs
├── sdks/           # SDK implementations
│   ├── python/     # Python SDK
│   └── typescript/ # TypeScript SDK
└── schemas/        # API schemas and models
```

## 📋 Code Style

- **Python**
  - Follow PEP 8
  - Use type hints
  - Document functions with docstrings
  - Use snake_case for variable and function names

- **TypeScript**
  - Follow ESLint configuration
  - Use TypeScript strict mode
  - Document with JSDoc comments
  - Use CamelCase for variables and functions

## 🔄 Release Process

1. Version bumps follow [Semantic Versioning](https://semver.org/)
2. Changes are documented in CHANGELOG.md
3. Releases are tagged in Git
4. Packages are published to PyPI and npm

## ❓ Questions?

- Create a [GitHub Discussion](https://github.com/your-username/skribble-sdk/discussions)
- Check existing [Issues](https://github.com/your-username/skribble-sdk/issues)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License. 