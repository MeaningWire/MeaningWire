#!/usr/bin/env python3
"""Pre-release read-only CLI foundation for MeaningWire.

The CLI exposes public repository state and validation behavior. It does not
execute mappings, convert data, contact remote services, or imply stable API
compatibility.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import mapping_registry
import validate_contracts

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REGISTRY_PATH = ROOT / "schemas" / "registry.json"
DEFAULT_MAPPING_NAMESPACE = "urn:meaningwire:mapping"


class CLIError(ValueError):
    """Raised for deterministic user-facing CLI failures."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="emit machine-readable JSON",
    )


def emit(payload: Any, text: str, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(text)


def schema_entries() -> list[dict[str, Any]]:
    validate_contracts.validate_registry()
    registry = load_json(SCHEMA_REGISTRY_PATH)
    entries = registry["schemas"]
    return sorted(entries, key=lambda entry: entry["id"])


def reference_text(reference: dict[str, Any]) -> str:
    namespace = reference["namespace"]
    identifier = reference["id"]
    version = reference.get("version")
    return f"{namespace}:{identifier}:{version}" if version else f"{namespace}:{identifier}"


def error_path(error: Any) -> str:
    path = "$"
    for item in error.absolute_path:
        if isinstance(item, int):
            path += f"[{item}]"
        else:
            path += f".{item}"
    return path


def cmd_doctor(args: argparse.Namespace) -> int:
    try:
        import validate_jsonschema
    except ModuleNotFoundError as exc:
        raise CLIError(
            "standards validator dependency is missing; install requirements-validation.txt"
        ) from exc

    schema_count = validate_contracts.validate_registry()
    bootstrap_valid, bootstrap_invalid = validate_contracts.validate_fixture_manifest()
    standards_schema_count = validate_jsonschema.validate_registered_schemas()
    standards_valid, standards_invalid = validate_jsonschema.validate_fixture_manifest()
    mapping_count = len(mapping_registry.load_records())

    payload = {
        "status": "PASS",
        "schemas": {
            "bootstrap_registered": schema_count,
            "draft_2020_12_registered": standards_schema_count,
        },
        "fixtures": {
            "bootstrap": {"valid_accepted": bootstrap_valid, "invalid_rejected": bootstrap_invalid},
            "draft_2020_12": {"valid_accepted": standards_valid, "invalid_rejected": standards_invalid},
        },
        "mappings": {"registered": mapping_count},
        "network_access": False,
    }
    text = (
        "PASS: MeaningWire doctor; "
        f"{schema_count} schemas registered; "
        f"{mapping_count} mappings registered; "
        f"{bootstrap_valid + standards_valid} validation-layer valid-fixture checks passed; "
        f"{bootstrap_invalid + standards_invalid} validation-layer invalid-fixture checks rejected as expected; "
        "network access disabled."
    )
    emit(payload, text, json_output=args.json_output)
    return 0


def cmd_schemas_list(args: argparse.Namespace) -> int:
    entries = schema_entries()
    payload = {"schemas": entries}
    lines = [f"{entry['id']}\t{entry['path']}\t{entry['version']}" for entry in entries]
    emit(payload, "\n".join(lines), json_output=args.json_output)
    return 0


def cmd_schema_validate(args: argparse.Namespace) -> int:
    try:
        import validate_jsonschema
    except ModuleNotFoundError as exc:
        raise CLIError(
            "standards validator dependency is missing; install requirements-validation.txt"
        ) from exc

    instance_path = Path(args.instance).expanduser()
    if not instance_path.is_file():
        raise CLIError(f"instance file does not exist: {args.instance}")

    registry, schemas = validate_jsonschema.build_registry()
    validator = validate_jsonschema.validator_for(args.schema_id, registry, schemas)
    instance = load_json(instance_path)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (list(error.absolute_path), error.message),
    )

    if errors:
        details = [
            {"path": error_path(error), "message": error.message}
            for error in errors
        ]
        payload = {
            "status": "INVALID",
            "schema_id": args.schema_id,
            "instance": str(instance_path),
            "errors": details,
        }
        if args.json_output:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"INVALID: {args.instance} against {args.schema_id}", file=sys.stderr)
            for detail in details:
                print(f"  {detail['path']}: {detail['message']}", file=sys.stderr)
        return 2

    payload = {
        "status": "VALID",
        "schema_id": args.schema_id,
        "instance": str(instance_path),
    }
    emit(
        payload,
        f"VALID: {args.instance} against {args.schema_id}",
        json_output=args.json_output,
    )
    return 0


def mapping_summary(mapping: dict[str, Any]) -> dict[str, Any]:
    return {
        "mapping_id": mapping["mapping_id"],
        "version": mapping["version"],
        "source": {
            "contract": mapping["source"]["contract"],
            "path": mapping["source"]["path"],
        },
        "target": {
            "contract": mapping["target"]["contract"],
            "path": mapping["target"]["path"],
        },
        "relationship": mapping["relationship"],
        "maturity": mapping["maturity"],
    }


def cmd_mappings_list(args: argparse.Namespace) -> int:
    mappings = mapping_registry.list_mappings()
    summaries = [mapping_summary(mapping) for mapping in mappings]
    payload = {"mappings": summaries}
    lines = [
        "\t".join(
            [
                reference_text(item["mapping_id"]),
                f"{reference_text(item['source']['contract'])}{item['source']['path']}",
                f"{reference_text(item['target']['contract'])}{item['target']['path']}",
                item["relationship"],
                item["maturity"],
            ]
        )
        for item in summaries
    ]
    emit(payload, "\n".join(lines), json_output=args.json_output)
    return 0


def cmd_mappings_inspect(args: argparse.Namespace) -> int:
    mapping = mapping_registry.get_mapping(args.namespace, args.identifier, args.version)
    emit(
        mapping,
        json.dumps(mapping, indent=2, sort_keys=True),
        json_output=args.json_output,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meaningwire",
        description="MeaningWire pre-release read-only inspection and validation CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="MeaningWire CLI EXPERIMENTAL 0.0.1",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="validate public registry and fixture health")
    add_json_flag(doctor)
    doctor.set_defaults(handler=cmd_doctor)

    schemas = commands.add_parser("schemas", help="inspect the schema registry")
    schema_commands = schemas.add_subparsers(dest="schemas_command", required=True)
    schemas_list = schema_commands.add_parser("list", help="list registered schemas")
    add_json_flag(schemas_list)
    schemas_list.set_defaults(handler=cmd_schemas_list)

    schema = commands.add_parser("schema", help="validate instances against registered schemas")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_validate = schema_commands.add_parser("validate", help="validate a local JSON instance")
    schema_validate.add_argument("schema_id", help="registered MeaningWire schema ID")
    schema_validate.add_argument("instance", help="path to a local JSON instance")
    add_json_flag(schema_validate)
    schema_validate.set_defaults(handler=cmd_schema_validate)

    mappings = commands.add_parser("mappings", help="inspect the mapping registry")
    mapping_commands = mappings.add_subparsers(dest="mappings_command", required=True)
    mappings_list = mapping_commands.add_parser("list", help="list registered mappings")
    add_json_flag(mappings_list)
    mappings_list.set_defaults(handler=cmd_mappings_list)

    mappings_inspect = mapping_commands.add_parser("inspect", help="inspect one registered mapping")
    mappings_inspect.add_argument("identifier", help="mapping identifier")
    mappings_inspect.add_argument(
        "--namespace",
        default=DEFAULT_MAPPING_NAMESPACE,
        help=f"mapping namespace (default: {DEFAULT_MAPPING_NAMESPACE})",
    )
    mappings_inspect.add_argument("--version", help="mapping version; required if identity is ambiguous")
    add_json_flag(mappings_inspect)
    mappings_inspect.set_defaults(handler=cmd_mappings_inspect)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (CLIError, validate_contracts.ContractValidationError, mapping_registry.MappingRegistryError, OSError, ValueError) as exc:
        if getattr(args, "json_output", False):
            print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
