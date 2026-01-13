# Lambda Testing Guide

## Local Testing

### 1. Test with Python directly
```bash
python test_lambda.py
```

### 2. Test with Docker (Lambda Runtime Interface Emulator)
```bash
# Build and run
docker-compose -f docker-compose.lambda.yml up --build

# Test in another terminal
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"httpMethod":"GET","path":"/","headers":{},"body":null}'
```

### 3. Test specific endpoints
```bash
# Health check
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"httpMethod":"GET","path":"/health","headers":{},"body":null}'

# Calculator endpoint
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod":"POST",
    "path":"/api/v1/calculator/calculate",
    "headers":{"Content-Type":"application/json"},
    "body":"{\"employment_type\":\"employee\",\"gross_salary\":10000}"
  }'
```

## AWS Testing

### 1. Deploy to AWS
```bash
./deploy.sh
```

### 2. Test via AWS CLI
```bash
aws lambda invoke \
  --function-name mastik-calculator \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json
```

### 3. Test via API Gateway (after CloudFormation deployment)
```bash
# Get API URL from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name mastik-calculator-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Test endpoints
curl $API_URL/health
curl -X POST $API_URL/api/v1/calculator/calculate \
  -H "Content-Type: application/json" \
  -d '{"employment_type":"employee","gross_salary":10000}'
```