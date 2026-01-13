import json
from lambda_handler import handler

# Test event for API Gateway
test_event = {
    "httpMethod": "GET",
    "path": "/",
    "headers": {},
    "queryStringParameters": None,
    "body": None,
    "isBase64Encoded": False,
    "requestContext": {
        "requestId": "test-request-id",
        "stage": "test"
    }
}

# Test the handler
response = handler(test_event, {})
print(json.dumps(response, indent=2))