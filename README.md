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
│   ├── models/
│   │   └── calculator.py       # Pydantic models (CalculatorInputs, results)
│   ├── services/               # Calculation logic (taxes, credits)
│   │   ├── tax_calculator.py
│   │   ├── multi_source_calculator.py
│   │   └── self_employed_calculator.py
│   ├── routers/                # API routes
│   │   └── calculator.py
│   └── utils/
│       └── tax_constants.py    # Tax brackets, rates, constants
├── requirements.txt
├── lambda_handler.py           # AWS Lambda handler
├── Dockerfile                  # Docker for app
├── Dockerfile.lambda           # Docker for Lambda
├── docker-compose.lambda.yml   # Compose for Lambda testing
├── cloudformation.yml          # AWS CloudFormation template for deployment
├── iam-policy.json             # IAM policy for Lambda execution
├── lambda-ecr-policy.json      # ECR policy for Lambda
├── deploy.sh                   # Deployment script
```

Key files:

- `app/services/tax_calculator.py` — credit points, income-tax, NI, health tax and pension calculations.
- `app/utils/tax_constants.py` — values for tax brackets, rates, and credit-point monetary value.

## Lambda & AWS Deployment

- **CloudFormation**: `cloudformation.yml` defines the complete infrastructure.
- **Docker**: `Dockerfile.lambda` builds a Lambda container image; use `docker-compose.lambda.yml` for local testing.
- **Deploy**: Use `deploy.sh` to push to AWS.

## Tests

- Unit tests: `pytest -q`

```bash
python -m pytest -q
```

## Development notes

- Use `app.models.calculator.CalculatorInputs` when crafting API requests; it documents all supported fields for credit calculation (children, spouse, education, immigration, foreign worker, etc.).
- Credit points logic is implemented in `app/services/tax_calculator.py::calculate_credit_points`.
- The default `uvicorn` invocation should use `app.main:app` from the repo root.
