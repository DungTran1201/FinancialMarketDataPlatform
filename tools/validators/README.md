# Documentation Validator Compatibility Runner (`tools/validators/`)

Legacy Documentation V1 multi-script validators were replaced in Documentation V2 by `scripts/docs/validate_docs.py`.

`run_all.py` remains here as a thin compatibility wrapper so existing CI pipelines (`.github/workflows/ci.yml`), `run.bat`, `setup.bat`, and `tools/hooks/stop_readiness_check.py` continue to work cleanly without breaking workflows.

## Usage

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
# Or via legacy compatibility wrapper:
.\.venv\Scripts\python.exe tools/validators/run_all.py
```
