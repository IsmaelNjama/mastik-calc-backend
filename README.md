# MASTIK Calculator Backend

FastAPI backend implementing an Israeli net-salary calculator and credit-points logic.

## Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run locally

- Start the FastAPI app (recommended):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: GET /health
- Root: GET /

## API (key endpoints)

- POST /api/v1/calculator/calculate
  - Calculate net salary and credit points. Body follows the `CalculatorInputs` model (see `app/models/calculator.py`).
- GET /api/v1/calculator/tax-brackets
  - Returns configured tax brackets.
- GET /api/v1/calculator/constants
  - Returns constants such as national insurance and credit point values.

Example `POST /api/v1/calculator/calculate` payload (minimal):

```json
{
  "employment_type": "employee",
  "gross_salary": 15000.0,
  "pension_rate": 6.0,
  "age": 31,
  "gender": "other"
}
```

## Project layout

```
/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/                 # Pydantic models (CalculatorInputs, results)
│   ├── services/               # Calculation logic (taxes, credits)
│   └── routers/                # API routes
├── lambda_handler.py           # AWS Lambda handler (optional deploy)
├── requirements.txt
├── Dockerfile*                 # Docker images (app and lambda variants available)
├── run-lambda-local.sh         # helper for local lambda testing
└── tests (top-level):
		├── test_api.py
		└── test_lambda.py
```

Files of interest:

- `app/services/tax_calculator.py` — credit points, income-tax, NI, health tax and pension calculations.
- `app/utils/tax_constants.py` — values for brackets, rates, and credit-point monetary value.

## Lambda & Docker

- There are artifacts for building/deploying as Lambda: `Dockerfile.lambda`, `docker-compose.lambda.yml`, and `lambda_handler.py`.
- Use `run-lambda-local.sh` to exercise the handler locally (make it executable if needed).

## Tests

- Unit tests: `pytest -q`

```bash
python -m pytest -q
```

## Development notes

- Use `app.models.calculator.CalculatorInputs` when crafting API requests; it documents all supported fields for credit calculation (children, spouse, education, immigration, foreign worker, etc.).
- Credit points logic is implemented in `app/services/tax_calculator.py::calculate_credit_points`.
- The default `uvicorn` invocation should use `app.main:app` from the repo root.
