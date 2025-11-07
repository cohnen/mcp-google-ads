"""
Schema validation module for MCP Google Ads mutate operations
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError, Draft7Validator

SCHEMA_DIR = Path(__file__).parent

# Schema file mappings
SCHEMAS = {
    'create_pmax': 'create_pmax.json',
    'update_budget': 'update_budget.json',
    'set_target_roas': 'set_target_roas.json',
    'pause_campaign': 'pause_campaign.json',
    'enable_campaign': 'enable_campaign.json',
    'attach_merchant_center': 'attach_merchant_center.json',
}

_schema_cache = {}

def load_schema(schema_name: str) -> Dict[str, Any]:
    """
    Load a JSON schema by name

    Args:
        schema_name: Name of the schema (without .json extension)

    Returns:
        Parsed JSON schema dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    if schema_name in _schema_cache:
        return _schema_cache[schema_name]

    if schema_name not in SCHEMAS:
        raise ValueError(f"Unknown schema: {schema_name}. Available: {list(SCHEMAS.keys())}")

    schema_path = SCHEMA_DIR / SCHEMAS[schema_name]

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    _schema_cache[schema_name] = schema
    return schema

def validate_params(schema_name: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate parameters against a schema

    Args:
        schema_name: Name of the schema to validate against
        params: Parameters to validate

    Returns:
        Tuple of (is_valid, error_message)
        If is_valid is True, error_message will be empty string
        If is_valid is False, error_message contains validation error details
    """
    try:
        schema = load_schema(schema_name)
        validate(instance=params, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, f"Validation error: {e.message}\nPath: {'.'.join(str(p) for p in e.path)}"
    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}"

def get_schema_description(schema_name: str) -> str:
    """
    Get the description from a schema

    Args:
        schema_name: Name of the schema

    Returns:
        Schema description string
    """
    try:
        schema = load_schema(schema_name)
        return schema.get('description', 'No description available')
    except Exception as e:
        return f"Error loading schema: {str(e)}"

def list_available_schemas() -> list[str]:
    """
    List all available schema names

    Returns:
        List of schema names
    """
    return list(SCHEMAS.keys())

def get_required_fields(schema_name: str) -> list[str]:
    """
    Get list of required fields for a schema

    Args:
        schema_name: Name of the schema

    Returns:
        List of required field names
    """
    try:
        schema = load_schema(schema_name)
        return schema.get('required', [])
    except Exception:
        return []

def get_schema_examples(schema_name: str) -> Dict[str, Any]:
    """
    Extract example values from schema properties

    Args:
        schema_name: Name of the schema

    Returns:
        Dictionary with example values for each property
    """
    try:
        schema = load_schema(schema_name)
        examples = {}

        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            if 'examples' in prop_schema and prop_schema['examples']:
                examples[prop_name] = prop_schema['examples'][0]

        return examples
    except Exception:
        return {}
