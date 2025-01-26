#!/usr/bin/env python3
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set, Union
from collections import defaultdict
import sys

typescript_type_map = {
    "string": "string",
    "number": "number",
    "integer": "number",
    "boolean": "boolean",
    "object": "any",
    "array": "any[]",
    "union": "any",
    "Blob": "Blob"
}

def get_model_dependencies(model_name: str, model_data: dict, models: dict, visited: set = None) -> set:
    """Get all model dependencies for a given model."""
    if visited is None:
        visited = set()
    
    if model_name in visited:
        return set()
    
    visited.add(model_name)
    dependencies = set()
    
    for field_data in model_data.get("properties", {}).values():
        field_type = field_data.get("type")
        if field_type == "object":
            if "ref" in field_data:
                ref = field_data["ref"]
                if ref in models:
                    dependencies.add(ref)
                    dependencies.update(get_model_dependencies(ref, models[ref], models, visited))
        elif field_type == "array":
            items = field_data.get("items", {})
            if items.get("type") == "object" and "ref" in items:
                ref = items["ref"]
                if ref in models:
                    dependencies.add(ref)
                    dependencies.update(get_model_dependencies(ref, models[ref], models, visited))
        elif field_type in models:
            dependencies.add(field_type)
            dependencies.update(get_model_dependencies(field_type, models[field_type], models, visited))
    
    return dependencies

def sort_models_by_dependencies(models: dict) -> list:
    """Sort models by their dependencies."""
    # Build dependency graph
    graph = {}
    for model_name, model_data in models.items():
        graph[model_name] = get_model_dependencies(model_name, model_data, models)
    
    # Topological sort
    sorted_models = []
    visited = set()
    temp_visited = set()
    
    def visit(model_name):
        if model_name in temp_visited:
            raise ValueError(f"Circular dependency detected: {model_name}")
        if model_name in visited:
            return
        
        temp_visited.add(model_name)
        for dep in graph[model_name]:
            visit(dep)
        temp_visited.remove(model_name)
        visited.add(model_name)
        sorted_models.append(model_name)
    
    for model_name in models:
        if model_name not in visited:
            visit(model_name)
    
    return sorted_models

def get_typescript_type(type_def):
    if isinstance(type_def, str):
        return typescript_type_map.get(type_def, "any")
    
    if "type" not in type_def:
        if "ref" in type_def:
            return type_def["ref"]
        return "any"
    
    type_name = type_def["type"]
    
    if type_name == "array":
        item_def = type_def.get("items", {})
        if isinstance(item_def, dict):
            if "ref" in item_def:
                return f"{item_def['ref']}[]"
            elif item_def.get("type") == "object":
                return f"{get_typescript_type(item_def)}[]"
            else:
                return f"{get_typescript_type(item_def)}[]"
        else:
            return f"{get_typescript_type(item_def)}[]"
    
    if type_name == "object":
        if "ref" in type_def:
            return type_def["ref"]
        # If it's an object type with properties, generate an inline type
        if "properties" in type_def:
            props = []
            for prop_name, prop_def in type_def["properties"].items():
                prop_type = get_typescript_type(prop_def)
                required = prop_name in type_def.get("required", [])
                props.append(f"{prop_name}{'' if required else '?'}: {prop_type}")
            return "{ " + "; ".join(props) + " }"
        return "any"
    
    if type_name == "union":
        types = type_def.get("types", [])
        return " | ".join(types)
    
    return typescript_type_map.get(type_name, "any")

def generate_typescript_type(model_name: str, model_def: Dict[str, Any]) -> str:
    """Generate TypeScript type definition for a model."""
    lines = []
    lines.append(f"export type {model_name} = ")

    # Handle union types
    if model_def.get("type") == "union":
        types = model_def.get("types", [])
        lines[-1] += types[0] + " | " + types[1]
        return "\n".join(lines)

    # Handle array types
    if model_def.get("type") == "array":
        item_def = model_def["items"]
        if isinstance(item_def, dict) and item_def.get("type") == "object":
            # Array of objects - define the object type inline
            lines[-1] += "{"
            for prop_name, prop_def in item_def["properties"].items():
                prop_type = get_typescript_type(prop_def)
                required = prop_name in item_def.get("required", [])
                lines.append(f"  {prop_name}{'' if required else '?'}: {prop_type};")
            lines.append("}[]")
        else:
            # Simple array type
            item_type = get_typescript_type(item_def)
            lines[-1] += f"{item_type}[]"
        return "\n".join(lines)

    # Regular object type
    lines[-1] += "{"
    required_fields = model_def.get("required", [])
    for prop_name, prop_def in model_def.get("properties", {}).items():
        prop_type = get_typescript_type(prop_def)
        # Use the alias if defined, otherwise use the original property name
        field_name = prop_def.get("alias", prop_name)
        # If the field name contains a hyphen, wrap it in quotes
        if "-" in field_name:
            field_name = f'"{field_name}"'
        lines.append(f"  {field_name}{'' if prop_name in required_fields else '?'}: {prop_type};")
    lines.append("}")

    return "\n".join(lines)

def get_field_type(field_data: Dict[str, Any], models: Dict[str, Any]) -> str:
    """Get the Python type for a field."""
    field_type = field_data.get("type", "Any")
    
    if field_type == "array":
        items = field_data.get("items", {})
        item_type = items.get("type", "Any")
        if item_type == "object" and "ref" in items:
            return f'List["' + items["ref"] + '"]'  # Use string literal for forward reference
        elif item_type == "string":
            return "List[str]"
        elif item_type == "number":
            return "List[float]"
        elif item_type == "integer":
            return "List[int]"
        elif item_type == "boolean":
            return "List[bool]"
        elif item_type in models:
            return f'List["' + item_type + '"]'  # Use string literal for model references in arrays
        return f"List[{item_type}]"
    elif field_type == "object" and "ref" in field_data:
        return f'"{field_data["ref"]}"'  # Use string literal for forward reference
    elif field_type == "string":
        return "str"
    elif field_type == "number":
        return "float"
    elif field_type == "integer":
        return "int"
    elif field_type == "boolean":
        return "bool"
    elif field_type in models:
        return f'"{field_type}"'  # Use string literal for forward reference
    
    return "Any"

def generate_pydantic_model(model_name: str, model_data: Dict[str, Any], models: Dict[str, Any]) -> str:
    """Generate a Pydantic model class definition."""
    lines = []
    
    # Add class definition with docstring
    lines.append(f"class {model_name}(BaseModel):")
    if "description" in model_data:
        lines.append(f'    """{model_data["description"]}"""')
    else:
        lines.append('    """Generated model."""')
        
    # Handle union types
    if model_data.get("type") == "union":
        types = model_data.get("types", [])
        # Map types to Python types
        type_map = {"string": "str", "Blob": "bytes"}
        python_types = [type_map.get(t, t) for t in types]
        type_str = ", ".join(python_types)
        if model_name == "DocumentContent":
            # Special case for DocumentContent to match SDK usage
            lines.append(f"    content: Union[{type_str}]")
            lines.append("    def __init__(self, content: Union[bytes, str]):")
            lines.append("        super().__init__(content=content)")
            lines.append("")
            lines.append("    @property")
            lines.append("    def raw_bytes(self) -> bytes:")
            lines.append('        """Get content as raw bytes."""')
            lines.append("        if isinstance(self.content, bytes):")
            lines.append("            return self.content")
            lines.append("        import base64")
            lines.append("        return base64.b64decode(self.content)")
            lines.append("")
            lines.append("    @property")
            lines.append("    def base64(self) -> str:")
            lines.append('        """Get content as base64 string."""')
            lines.append("        if isinstance(self.content, str):")
            lines.append("            return self.content")
            lines.append("        import base64")
            lines.append("        return base64.b64encode(self.content).decode()")
            lines.append("")
        else:
            lines.append(f"    value: Union[{type_str}]")

    # Handle array types
    if model_data.get("type") == "array":
        item_def = model_data["items"]["type"]
        if item_def == "object":
            # For array of objects, just create the item model
            nested_props = model_data["items"].get("properties", {})
            nested_required = model_data["items"].get("required", [])
            model_data = {
                "type": "object",
                "properties": nested_props,
                "required": nested_required,
                "description": model_data.get("description", "")
            }
            # Continue with regular object handling
        else:
            # Skip primitive array types
            return ""

    # Handle regular object types
    if not model_data.get("properties"):
        return "\n".join(lines)
        
    required_fields = model_data.get("required", [])
    
    # Process properties
    for prop_name, prop_data in model_data["properties"].items():
        field_type = get_field_type(prop_data, models)
        field_kwargs = {}
        
        # Handle optional fields
        is_optional = prop_name not in required_fields
        if is_optional:
            field_type = f"Optional[{field_type}]"
            field_kwargs["default"] = None
            
        # Add description if present
        if "description" in prop_data:
            field_kwargs["description"] = prop_data["description"]
            
        # Add any default value
        if "default" in prop_data:
            field_kwargs["default"] = prop_data["default"]
            
        # Build the field constructor string
        if field_kwargs:
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in field_kwargs.items())
            lines.append(f"    {prop_name}: {field_type} = Field({kwargs_str})")
        else:
            lines.append(f"    {prop_name}: {field_type}")
            
    return "\n".join(lines)

def generate_mdx_documentation(models: Dict[str, Any]) -> str:
    """Generate MDX documentation for types."""
    lines = [
        "---",
        "title: 'Types Reference'",
        "description: 'Complete reference for all types and models in the Skribble SDK'",
        "---",
        "",
        "All types are provided by the SDK - you don't need to define them yourself. Import them as follows:",
        "",
        "<CodeGroup>",
        "```python Python",
        "from skribble.models import Document, SignatureRequest, Seal, SignerIdentityData, VisualSignature",
        "```",
        "",
        "```typescript TypeScript",
        "import { Types } from 'skribble-sdk';",
        "```",
        "</CodeGroup>",
        ""
    ]

    # Group models by category
    categories = {
        "Common Types": ["Position", "Image"],
        "Document Types": ["Document", "DocumentRequest", "DocumentResponse"],
        "Signature Request Types": ["SignatureRequest", "Signature", "SignerIdentityData", "VisualSignature", "SignatureResponse", "SignatureRequestResponse"],
        "Seal Types": ["Seal", "SealRequest", "SealResponse"],
        "Attachment Types": ["Attachment", "AttachmentRequest", "AttachmentResponse"]
    }

    # Generate documentation for each category
    for category, model_names in categories.items():
        lines.extend([
            f"## {category}",
            ""
        ])

        for model_name in model_names:
            if model_name not in models:
                continue

            model_data = models[model_name]
            description = model_data.get("description", "")
            lines.extend([
                f"### {model_name}",
                description + "\n" if description else "",
            ])

            if "properties" in model_data:
                required_fields = model_data.get("required", [])
                for field_name, field_data in model_data["properties"].items():
                    field_type = get_typescript_type(field_data)
                    description = field_data.get("description", "")
                    is_required = field_name in required_fields
                    default_value = field_data.get("default")
                    
                    # Start ResponseField component
                    field_props = [
                        f'name="{field_name}"',
                        f'type="{field_type}"'
                    ]
                    
                    if is_required:
                        field_props.append('required')
                    
                    if default_value is not None:
                        field_props.append(f'default="{default_value}"')
                    
                    # If there's a description, use opening and closing tags
                    if description:
                        lines.append(f"<ResponseField {' '.join(field_props)}>")
                        lines.append(f"  {description}")
                        lines.append("</ResponseField>")
                    else:
                        # If no description, use self-closing tag
                        lines.append(f"<ResponseField {' '.join(field_props)} />")
                    
                    lines.append("")

            lines.append("")

    return "\n".join(lines)

def generate_operation_docs(operation_name: str, operation_data: Dict[str, Any], models: Dict[str, Any]) -> str:
    """Generate documentation for an API operation including request/response types."""
    lines = []
    
    # Get request and response types from operation data
    request_type = operation_data.get("request_type")
    response_type = operation_data.get("response_type")
    
    if request_type and request_type in models:
        lines.extend([
            "",
            "<ResponseField name=\"request\" type=\"Request Object\">",
            f"  <Expandable title=\"{request_type} properties\">",
        ])
        
        model_data = models[request_type]
        required_fields = model_data.get("required", [])
        
        for field_name, field_data in model_data.get("properties", {}).items():
            field_type = get_typescript_type(field_data)
            description = field_data.get("description", "")
            is_required = field_name in required_fields
            
            field_props = [
                f'name="{field_name}"',
                f'type="{field_type}"'
            ]
            if is_required:
                field_props.append('required')
            
            # If there's a description, use opening and closing tags with description
            if description:
                lines.append(f"    <ResponseField {' '.join(field_props)}>")
                lines.append(f"      {description}")
                lines.append("    </ResponseField>")
            else:
                # If no description, use self-closing tag
                lines.append(f"    <ResponseField {' '.join(field_props)} />")
            
        lines.extend([
            "  </Expandable>",
            "</ResponseField>",
            ""
        ])
    
    if response_type and response_type in models:
        lines.extend([
            "",
            "<ResponseField name=\"response\" type=\"Response Object\">",
            f"  <Expandable title=\"{response_type} properties\">",
        ])
        
        model_data = models[response_type]
        required_fields = model_data.get("required", [])
        
        for field_name, field_data in model_data.get("properties", {}).items():
            field_type = get_typescript_type(field_data)
            description = field_data.get("description", "")
            is_required = field_name in required_fields
            
            field_props = [
                f'name="{field_name}"',
                f'type="{field_type}"'
            ]
            if is_required:
                field_props.append('required')
            
            # If there's a description, use opening and closing tags with description
            if description:
                lines.append(f"    <ResponseField {' '.join(field_props)}>")
                lines.append(f"      {description}")
                lines.append("    </ResponseField>")
            else:
                # If no description, use self-closing tag
                lines.append(f"    <ResponseField {' '.join(field_props)} />")
            
        lines.extend([
            "  </Expandable>",
            "</ResponseField>",
            ""
        ])
    
    return "\n".join(lines)

def generate_api_documentation(models: Dict[str, Any], operations: Dict[str, Any]) -> Dict[str, str]:
    """Generate API documentation for all operations."""
    docs = {}
    
    # Generate documents.mdx
    docs["documents"] = [
        "---",
        "title: 'Documents'",
        "description: 'API reference for document operations'",
        "---",
        ""
    ]
    
    for op_name, op_data in operations.get("documents", {}).items():
        docs["documents"].extend([
            f"## {op_data['title']}",
            "",
            op_data.get("description", ""),
            "",
            "<CodeGroup>",
            "```python Python",
            op_data["python_signature"],
            "```",
            "",
            "```typescript TypeScript",
            op_data["typescript_signature"],
            "```",
            "</CodeGroup>",
        ])
        docs["documents"].append(generate_operation_docs(op_name, op_data, models))
    
    # Generate signature-requests.mdx (note the hyphen instead of underscore)
    docs["signature-requests"] = [
        "---",
        "title: 'Signature Requests'",
        "description: 'API reference for signature request operations'",
        "---",
        ""
    ]
    
    for op_name, op_data in operations.get("signature_requests", {}).items():
        docs["signature-requests"].extend([
            f"## {op_data['title']}",
            "",
            op_data.get("description", ""),
            "",
            "<CodeGroup>",
            "```python Python",
            op_data["python_signature"],
            "```",
            "",
            "```typescript TypeScript",
            op_data["typescript_signature"],
            "```",
            "</CodeGroup>",
        ])
        docs["signature-requests"].append(generate_operation_docs(op_name, op_data, models))
    
    # Generate seals.mdx
    docs["seals"] = [
        "---",
        "title: 'Seals'",
        "description: 'API reference for seal operations'",
        "---",
        ""
    ]
    
    for op_name, op_data in operations.get("seals", {}).items():
        docs["seals"].extend([
            f"## {op_data['title']}",
            "",
            op_data.get("description", ""),
            "",
            "<CodeGroup>",
            "```python Python",
            op_data["python_signature"],
            "```",
            "",
            "```typescript TypeScript",
            op_data["typescript_signature"],
            "```",
            "</CodeGroup>",
        ])
        docs["seals"].append(generate_operation_docs(op_name, op_data, models))
    
    return {k: "\n".join(v) for k, v in docs.items()}

def generate_models(schema_path: str, ts_output_path: str, py_output_path: str, mdx_output_path: str, operations_path: str, docs_dir: str):
    """Generate TypeScript and Python models from a YAML schema."""
    print("\nGenerating models from schema...")
    print(f"Schema path: {schema_path}")
    print(f"Exists: {os.path.exists(schema_path)}\n")

    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)

    print("Loading schema...")
    with open(schema_path, "r") as f:
        schema = yaml.safe_load(f)
    
    if not isinstance(schema, dict):
        print(f"\nError: Schema must be a dictionary, got {type(schema)}")
        print("Schema content:", schema)
        return
    
    if "models" not in schema:
        print("\nError: Schema must have a 'models' key")
        print("Available keys:", list(schema.keys()))
        return
    
    models = schema["models"]
    if not isinstance(models, dict):
        print(f"\nError: Models must be a dictionary, got {type(models)}")
        print("Models content:", models)
        return
    
    print(f"Found {len(models)} models in schema")
    
    # Check for forward references
    print("\nChecking model dependencies...")
    forward_refs = set()
    seen_models = set()

    for model_name, model_data in models.items():
        seen_models.add(model_name)
        for field_data in model_data.get("properties", {}).values():
            field_type = field_data.get("type")
            if field_type == "object" and "ref" in field_data:
                ref = field_data["ref"]
                if ref not in seen_models:
                    forward_refs.add((model_name, ref))
            elif field_type == "array":
                items = field_data.get("items", {})
                if items.get("type") == "object" and "ref" in items:
                    ref = items["ref"]
                    if ref not in seen_models:
                        forward_refs.add((model_name, ref))
            elif field_type in models and field_type not in seen_models:
                forward_refs.add((model_name, field_type))

    # Error out if forward references are found
    if forward_refs:
        print("\nError: Found models that reference other models that haven't been defined yet:")
        for model, ref in forward_refs:
            print(f"  - {model} references {ref}")
        print("\nTo fix this, move the referenced models before the models that reference them in the schema file.")
        print("For example, move SignerIdentityData before SignatureResponse.")
        sys.exit(1)
    
    # Generate Python models
    print("\nGenerating Python models...")
    py_lines = [
        "# ----------------------------------------",
        "# THIS FILE IS GENERATED - DO NOT EDIT",
        "# Run generator via: pnpm generate-models",
        "# Source: schemas/models.yaml",
        "# ----------------------------------------",
        "",
        "from typing import List, Optional, Any, Union",
        "from pydantic import BaseModel, Field",
        "from enum import Enum",
        "from difflib import get_close_matches",
        "from .exceptions import SkribbleValidationError",
        "",
        "# Type aliases",
        "Blob = bytes",
        "",
    ]
    
    # Generate each model in the order they appear in the schema
    for model_name, model_data in models.items():
        print(f"  - Generating {model_name}")
        py_lines.append(generate_pydantic_model(model_name, model_data, models))
        py_lines.append("")
    
    # Write Python models
    print(f"\nWriting Python models to {py_output_path}")
    with open(py_output_path, "w") as f:
        f.write("\n".join(py_lines))
    
    # Generate TypeScript models
    print("\nGenerating TypeScript models...")
    ts_lines = [
        "// ----------------------------------------",
        "// THIS FILE IS GENERATED - DO NOT EDIT",
        "// Run generator via: pnpm generate-models",
        "// Source: schemas/models.yaml",
        "// ----------------------------------------",
        "",
    ]
    for model_name, model_data in models.items():
        print(f"  - Generating {model_name}")
        ts_lines.append(generate_typescript_type(model_name, model_data))
        ts_lines.append("")
    
    # Write TypeScript models
    print(f"\nWriting TypeScript models to {ts_output_path}")
    with open(ts_output_path, "w") as f:
        f.write("\n".join(ts_lines))

    # Generate MDX documentation
    print("\nGenerating MDX documentation...")
    mdx_content = generate_mdx_documentation(models)
    
    # Write MDX documentation
    print(f"\nWriting MDX documentation to {mdx_output_path}")
    with open(mdx_output_path, "w") as f:
        f.write(mdx_content)
    
    # Load operations schema
    print("\nLoading operations schema...")
    with open(operations_path, "r") as f:
        operations = yaml.safe_load(f)

    # Generate API documentation
    print("\nGenerating API documentation...")
    api_docs = generate_api_documentation(models, operations)
    
    # Write API documentation files
    for doc_type, content in api_docs.items():
        doc_path = os.path.join(docs_dir, f"{doc_type}.mdx")
        print(f"\nWriting {doc_type} documentation to {doc_path}")
        with open(doc_path, "w") as f:
            f.write(content)

    print("\nDone!")

def main():
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths
    schema_path = os.path.abspath(os.path.join(script_dir, "..", "..", "schemas", "models.yaml"))
    operations_path = os.path.abspath(os.path.join(script_dir, "..", "..", "schemas", "operations.yaml"))
    ts_output_path = os.path.abspath(os.path.join(script_dir, "..", "..", "sdks", "typescript", "src", "types.ts"))
    py_output_path = os.path.abspath(os.path.join(script_dir, "..", "..", "sdks", "python", "skribble", "models.py"))
    mdx_output_path = os.path.abspath(os.path.join(script_dir, "..", "..", "docs", "api-reference", "types.mdx"))
    docs_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "docs", "api-reference"))

    generate_models(schema_path, ts_output_path, py_output_path, mdx_output_path, operations_path, docs_dir)

if __name__ == "__main__":
    main() 