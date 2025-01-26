# Skribble Schema Validation

JSON Schema definitions for validating Skribble SDK schema files:
- `models.schema.json`: Validates the model definitions in `schemas/models.yaml`
- `operations.schema.json`: Validates the API operations in `schemas/operations.yaml`

## Usage

Install dependencies:
```bash
pnpm install
```

Validate schemas:
```bash
pnpm validate
```

## IDE Integration

For real-time validation in VS Code:
1. Install the "YAML" extension by Red Hat
2. Add these settings to your `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    "./packages/schema-validation/models.schema.json": ["schemas/models.yaml"],
    "./packages/schema-validation/operations.schema.json": ["schemas/operations.yaml"]
  }
}
``` 