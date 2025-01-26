# Skribble SDK

A TypeScript SDK for interacting with the Skribble API.

## Installation

You can install the Skribble SDK using npm:

```
npm install skribble-sdk
```

## Basic Usage

Here is a basic example of how to use the Skribble TypeScript SDK to create a signature request:

```typescript
import skribble from "skribble-sdk";

// Replace with your actual API credentials
const USERNAME = "your_username";
const API_KEY = "your_api_key";

# Initialize the SDK and get the access token
const token = skribble.init(USERNAME, API_KEY);
console.log(`Access token: ${token}`);

// Create a signature request
const signatureRequest = {
    "title": "Test Signature Request",
    "message": "Please sign this test document",
    "file_url": "https://pdfobject.com/pdf/sample.pdf",
    "signatures": [
        {
            "account_email": "signer1@example.com"
        }
    ],
}

const createResponse = skribble.signature_request.create(signatureRequest);
console.log(createResponse);
```

For more detailed examples and advanced usage, please refer to the [Documentation](https://skribblesdk.mintlify.app/typescript).