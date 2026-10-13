# Quantum Entanglement Witness

Numerical Peres–Horodecki positive-partial-transpose (PPT) analysis for **2×2 and 2×3 bipartite quantum density matrices**, plus a browser calculator for **two-qubit Bell-diagonal states**.

## Features

- Checks input density matrices for dimensions, finite elements, Hermiticity, unit trace and positive semidefiniteness.
- Computes eigenvalues of the partial transpose on subsystem B and **negativity** (sum of absolute values of negative eigenvalues).
- Classifies supported states as entangled (NPT) or separable (PPT). In 2×2 and 2×3 dimensions the PPT criterion is necessary and sufficient.
- For NPT states, constructs an entanglement witness `W = (|v⟩⟨v|)ᵀᴮ` from a negative partial-transpose eigenvector and returns its expectation value.
- Includes JSON CLI and FastAPI endpoints.
- Includes a standalone client-side [browser calculator](index.html) for Bell-diagonal two-qubit states (no backend required).
- Retains the original generic threshold-based telemetry, audit and batch commands for compatibility. **Those legacy commands are not quantum PPT calculations.**

## Browser application

Open `index.html` in a current desktop or mobile browser, or serve the repository root over HTTP. Select a preset or enter four Bell-state probabilities that sum to 1; the page computes the PPT eigenvalue spectrum, negativity, witness expectation and 4×4 state matrix. Results can be exported as JSON.

The static-site deployment workflow is in `.github/workflows/pages.yml`. GitHub Pages must be enabled with **GitHub Actions** as its source in repository settings; the live address is not advertised until deployment is confirmed.

**Privacy:** The browser calculator runs without API calls, tracking, browser storage or uploads. The Python API runs calculations on the server where you install it; do not deploy the unauthenticated API on a public network.

## Install

Requires Python 3.9 or newer. From the repository root:

```bash
python -m pip install -e ".[server,test]"
python -m pytest -q
```

For the numerical Python API alone, `python -m pip install -e .` installs NumPy and Pydantic. The optional `server` extra installs FastAPI and Uvicorn.

## Calculate a PPT witness

```bash
quantum-entanglement-witness ppt --input examples/bell_state.json
# Equivalent, when running the source checkout:
python cli.py ppt --input examples/bell_state.json
```

Expected for the supplied Bell state: partial-transpose eigenvalues `[-0.5, 0.5, 0.5, 0.5]`, negativity `0.5`, classification `entangled`, and witness expectation `-0.5`.

Python usage:

```python
from entanglement_witness.ppt import analyze_density_matrix

rho = [
    [0.5, 0, 0, 0.5],
    [0,   0, 0,   0],
    [0,   0, 0,   0],
    [0.5, 0, 0, 0.5],
]
print(analyze_density_matrix(rho, dimensions=(2, 2)))
```

Complex matrix elements can be provided as `[real, imaginary]` pairs in JSON. The basis ordering is `|a,b⟩` with subsystem B as the transposed subsystem; allowed dimensions are `[2,2]`, `[2,3]` and `[3,2]`.

A non-physical matrix is rejected rather than silently normalized. Numerical classification uses a tolerance of `1e-9`; experimental reconstructions should be validated with an uncertainty model instead of treating borderline eigenvalues as conclusive.

## HTTP API

```bash
# Set AUDIT_SECRET_KEY only if using legacy audit endpoints:
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000

curl --fail -X POST http://127.0.0.1:8000/api/ppt \
  -H 'Content-Type: application/json' \
  --data-binary @examples/bell_state.json
```

`POST /api/ppt` performs the numerical analysis and returns HTTP 422 on an invalid matrix. `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /metrics` and `GET /api/audit/logs` remain for the **legacy operational interface**, which is not a quantum state analyzer.

## Legacy commands

```bash
python cli.py audit --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
```

These maintain backward compatibility with older threshold alerts and their in-memory HMAC audit chain. Set `AUDIT_SECRET_KEY` (at least 16 characters, generated randomly) before using audit operations. The audit records are not persisted across process restarts. The mock chat provider does not perform model inference or verify scientific claims.

## Tests, packaging and deployment

- Unit tests cover separable, entangled and complex states, qubit–qutrit dimensions, invalid inputs, API responses, legacy workflows and audit-signature tampering.
- GitHub Actions tests Python 3.10–3.12; dependencies are installed from `pyproject.toml`.
- A Dockerfile and `docker-compose.yml` are provided for the backend; do not expose the server publicly without authentication, access controls and appropriate key management.
- Static browser pages do not execute Python. The Bell-diagonal calculator uses closed-form matrix calculations in JavaScript, so Pyodide is not necessary.

## Scientific limitations

The PPT criterion is complete for bipartite **2×2 and 2×3** systems but not for arbitrary higher-dimensional or multipartite states. A positive partial transpose alone cannot exclude bound entanglement in larger dimensions. The browser accepts only Bell-diagonal states; it is not a general-purpose tomography, uncertainty-analysis or device-independent witness tool.

## License

MIT. See [LICENSE](LICENSE).
