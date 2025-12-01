# MASTIK Calculator Backend

FastAPI backend for the Israeli Net Salary Calculator.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/v1/calculator/calculate
Calculate net salary based on employment type and inputs.

### GET /api/v1/calculator/tax-brackets
Get current Israeli tax brackets.

### GET /api/v1/calculator/constants
Get all tax constants (national insurance, health tax, etc.).

## Project Structure

```
mastik_calc_backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── app/
│   ├── models/            # Pydantic models
│   │   └── calculator.py
│   ├── services/          # Business logic
│   │   ├── tax_calculator.py
│   │   ├── multi_source_calculator.py
│   │   └── self_employed_calculator.py
│   ├── routers/           # API routes
│   │   └── calculator.py
│   └── utils/             # Utilities and constants
│       └── tax_constants.py
```

## Features

- Employee salary calculation
- Multiple employers support
- Self-employed income calculation
- Combined employment (employee + self-employed)
- Israeli tax brackets and deductions for 2025
- Credit points calculation
- CORS enabled for frontend integration
