# Skribble SDK

A Python SDK for interacting with the Skribble API.

## Installation

You can install the Skribble SDK using pip:

```
pip install skribble-sdk
```

## Basic Usage

Here is a basic example of how to use the Skribble Python SDK to create a signature request:

```python
import skribble

# Replace with your actual API credentials
USERNAME = "your_username"
API_KEY = "your_api_key"

# Initialize the SDK
skribble.init(USERNAME, API_KEY)

# Create a signature request
signature_request = {
    "title": "Test Signature Request",
    "message": "Please sign this test document",
    "file_url": "https://pdfobject.com/pdf/sample.pdf",
    "signatures": [
        {
            "account_email": "signer1@example.com"
        }
    ],
}

create_response = skribble.signature_request.create(signature_request)
print(create_response)
```

For more detailed examples and advanced usage, please refer to the [Examples](../docs/documentation/python/examples.mdx) section in our documentation.