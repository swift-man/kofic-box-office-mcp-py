# AGENTS.md

This repository hosts a Python MCP server for the dataset `영화진흥위원회_박스오피스`.

## Product Scope

- Support Streamable HTTP MCP only.
- Do not add `stdio`, `sse`, or transport-selection features unless explicitly requested.
- Keep the public MCP surface focused on the KOFIC box-office dataset exposed by `getKFCC0502`.

## Architecture

Follow SOLID boundaries when making changes.

- `src/kofic_box_office_mcp/server.py`
  - MCP registration and process startup only.
  - Keep tool handlers thin.
  - No HTTP request building, response parsing, or environment loading here.

- `src/kofic_box_office_mcp/bootstrap.py`
  - Composition root only.
  - Build settings, response parser, gateway, and service objects.

- `src/kofic_box_office_mcp/service.py`
  - Application/use-case layer.
  - Validate user inputs, normalize pagination arguments, and delegate to the gateway.
  - Depend on abstractions such as `KoficBoxOfficeGateway`, not concrete transport details.

- `src/kofic_box_office_mcp/gateway.py`
  - External API boundary.
  - Own HTTP transport concerns only.
  - Delegate payload decoding and normalization to `response_parser.py`.

- `src/kofic_box_office_mcp/response_parser.py`
  - Decode JSON or XML responses from the KOFIC box-office API.
  - Normalize payloads into the stable MCP-facing response shape.

- `src/kofic_box_office_mcp/settings.py`
  - Environment/config loading only.

- `src/kofic_box_office_mcp/runtime.py`
  - Streamable HTTP runtime config only.

- `src/kofic_box_office_mcp/reference.py`
  - Static/reference payload construction only.

- `src/kofic_box_office_mcp/validation.py`
  - Shared validation helpers only.

- `src/kofic_box_office_mcp/constants.py`
  - Static dataset metadata and output field definitions only.

## Change Rules

- Prefer extending the service and gateway layers over adding logic to MCP tool functions.
- If new API datasets are added later, create a focused service/gateway pair or a clearly separated adapter instead of stacking conditionals into the existing implementation.
- Keep error messages user-facing and actionable.
- Avoid framework-heavy abstractions. Use small protocols, dataclasses, and explicit composition.
- Preserve the Streamable HTTP default endpoint at `http://127.0.0.1:8000/mcp` unless there is a deliberate runtime change.

## Runtime Rules

- `scripts/run_http.sh` is the supported local launch path.
- `.env.example` must reflect the actually supported runtime variables.
- A change to `AGENTS.md` does not require restarting the MCP server by itself.
- If `AGENTS.md` changes, restart the coding-agent session or client so the new instructions are picked up.

## Restart Guidance

- If runtime code, service code, environment-variable handling, or dependency wiring changes, surface the restart commands in the response.
- If only `AGENTS.md` changed, do not tell the user to restart the MCP server.
- If only `AGENTS.md` changed, tell the user to restart the coding-agent session or client instead.

## Testing

Run these after meaningful changes:

```bash
bash -n scripts/run_http.sh
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Docs

- Update `README.md` when changing runtime behavior, environment variables, or launch steps.
- Keep examples aligned with Streamable HTTP at `http://127.0.0.1:8000/mcp` unless the default changes.
