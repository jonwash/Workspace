"""Validate product_spec.yaml against product_spec.schema.json.

    python3 spec/validate_spec.py spec/product_spec.yaml

Dev tooling only (not part of the shipped app). Needs two dev dependencies:

    pip install pyyaml jsonschema

Beyond schema validation, this also checks two cross-file invariants that a raw
JSON Schema can't express:
  - every interfaces.openapi operation named in the spec exists in openapi.yaml
  - every data_formats file referenced by the spec exists on disk

Exits non-zero on any failure so it can gate CI.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _need(mod, pip_name):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"validate_spec: missing dev dependency '{pip_name}'. "
                 f"Install with: pip install pyyaml jsonschema")


def main(spec_path):
    yaml = _need("yaml", "pyyaml")
    jsonschema = _need("jsonschema", "jsonschema")

    with open(spec_path) as f:
        spec = yaml.safe_load(f)
    with open(os.path.join(HERE, "product_spec.schema.json")) as f:
        schema = json.load(f)

    errors = []

    # 1. structural validation
    try:
        jsonschema.validate(spec, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"schema: {e.message} (at {'/'.join(str(p) for p in e.path)})")

    spec_dir = os.path.dirname(os.path.abspath(spec_path))

    # 2. every referenced data-format file exists
    for group in (spec.get("data_formats") or {}).values():
        for item in group:
            ref = item.get("file")
            if ref and not os.path.exists(os.path.join(spec_dir, ref)):
                errors.append(f"data_formats: referenced file not found: {ref}")

    # 3. every spec operation exists in the OpenAPI contract
    oa_file = spec.get("interfaces", {}).get("openapi", {}).get("file")
    if oa_file:
        oa_path = os.path.join(spec_dir, oa_file)
        if not os.path.exists(oa_path):
            errors.append(f"interfaces: openapi file not found: {oa_file}")
        else:
            with open(oa_path) as f:
                openapi = yaml.safe_load(f)
            declared = {
                op.get("operationId")
                for path in (openapi.get("paths") or {}).values()
                for op in path.values()
                if isinstance(op, dict) and "operationId" in op
            }
            for op in spec.get("interfaces", {}).get("openapi", {}).get("operations", []):
                oid = op.get("op_id")
                if oid and oid not in declared:
                    errors.append(f"interfaces: operation '{oid}' not found in {oa_file}")

    if errors:
        print(f"FAIL — {len(errors)} problem(s) in {spec_path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    stories = len(spec.get("stories", []))
    flows = len(spec.get("ux", {}).get("flows", []))
    print(f"OK — {spec_path} valid ({stories} stories, {flows} flows, "
          f"{len(spec.get('evaluation', {}).get('commands', []))} eval commands).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 spec/validate_spec.py <product_spec.yaml>")
    main(sys.argv[1])
