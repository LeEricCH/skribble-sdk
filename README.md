# Skribble SDK

[![Documentation](https://img.shields.io/badge/documentation-mintlify-teal.svg)](https://skribblesdk.mintlify.app/)
[![Python Version](https://img.shields.io/pypi/v/skribble-sdk.svg)](https://pypi.org/project/skribble-sdk/)
[![Python Tests](https://github.com/LeEricCH/skribble-sdk/actions/workflows/python-tests.yml/badge.svg)](https://github.com/LeEricCH/skribble-sdk/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/LeEricCH/skribble-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/LeEricCH/skribble-sdk)
[![Python Coverage](https://img.shields.io/badge/Python%20Coverage-84%25-green.svg)](https://codecov.io/gh/LeEricCH/skribble-sdk)
[![npm version](https://img.shields.io/npm/v/skribble-sdk.svg)](https://www.npmjs.com/package/skribble-sdk)
[![License](https://img.shields.io/github/license/LeEricCH/skribble-sdk.svg)](LICENSE)

A community-maintained SDK for Skribble's electronic signature API, available for both Python and TypeScript.

## 📦 Installation

**Python**
```bash
pip install skribble-sdk
```

**TypeScript/JavaScript**
```bash
npm install skribble-sdk
# or
yarn add skribble-sdk
# or
pnpm add skribble-sdk
```

## 📚 Documentation

Visit the [comprehensive documentation](https://skribblesdk.mintlify.app/) for:
- Quick Start Guide
- API Reference
- Code Examples
- Best Practices

## 🛠️ Project Structure

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

## 🧪 Test Coverage

- **Python**: Test coverage is almost complete.
- **TypeScript**: Test coverage has not yet started. Contributions are welcome!

## 🤝 Contributing

1. **Setup Development Environment**
   ```bash
   # Clone the repository
   git clone https://github.com/LeEricCH/skribble-sdk.git
   cd skribble-sdk

   # Install dependencies
   pnpm install
   ```

2. **Run Tests**
   ```bash
   pnpm test
   ```

3. **Generate Models**
   ```bash
   pnpm generate-models
   ```

4. **Build Documentation**
   ```bash
   pnpm docs:dev
   ```

See our [contribution guidelines](.github/CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is a community-maintained SDK and is not officially supported by Skribble. Use at your own discretion.

