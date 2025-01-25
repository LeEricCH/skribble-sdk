import skribble
from skribble import (
    SignatureRequest, 
    SkribbleAuthError, 
    SkribbleAPIError, 
    SkribbleValidationError, 
    SkribbleOperationError,
    AttachmentRequest
)
import requests
import base64
from termcolor import colored

# Replace these with your actual Skribble API credentials
# You can get these from your Skribble account settings
USERNAME: str = "api_demo_skribbleag_42b4_6" 
API_KEY: str = "87d93a7f-1fce-411a-9cca-dedce9a731bc"

if not USERNAME or not API_KEY:
    raise ValueError(
        "Please set your Skribble API credentials at the top of this file.\n"
        "You can find these in your Skribble account settings."
    )

try:
    # Initialize the SDK with username and API key
    access_token = skribble.init(username=USERNAME, api_key=API_KEY)
    print(colored("Successfully authenticated with Skribble API", "green"))
    print(colored(f"Access token: {access_token[:10]}...", "cyan"))

    # Reinitialize the SDK with the access token (not needed, just for demo purposes)
    skribble.init(access_token=access_token)

    # Create a sample signature request
    signature_request = {
        "title": "Test Signature Request",
        "message": "Please sign this test document",
        "file_url": "https://pdfobject.com/pdf/sample.pdf",
        "signatures": [
            {
                "account_email": "signer1@example.com",
                "signer_identity_data": {
                    "email_address": "signer1@example.com",
                    "mobile_number": "1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                    "language": "en"
                },
                "sequence": 1,
            },
            {
                "account_email": "signer2@example.com",
                "signer_identity_data": {
                    "email_address": "signer2@example.com",
                    "mobile_number": "0987654321",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "language": "en"
                },
                "sequence": 2,
            },
        ],
    }

    # Create a signature request
    create_response = skribble.signature_request.create(signature_request)
    print(colored("Signature request created successfully:", "green"))
    print(colored(create_response.model_dump(), "cyan"))

    # Remind signer about the signature request
    skribble.signature_request.remind(create_response.id)
    print(colored("Reminded signer about the signature request", "green"))

    signature_request_id = create_response.id

    # Add signer to the signature request
    add_signer_response = skribble.signature_request.signer.add(create_response.id, {
        "account_email": "test@test.com",
        "signer_identity_data": {
            "email_address": "test@test.com",
            "mobile_number": "1234567890",
            "first_name": "Test",
            "last_name": "User",
        },
        "language": "en"
    })
    print(colored("Signer added successfully:", "green"))
    print(colored(add_signer_response.model_dump(), "cyan"))

    # Get the created signature request to find the signer ID
    get_response = skribble.signature_request.get(signature_request_id)
    signer_to_remove = next((signer for signer in get_response.signatures 
                             if (hasattr(signer, 'signer_identity_data') and 
                                 signer.signer_identity_data and 
                                 signer.signer_identity_data.email_address == "signer2@example.com") or
                             signer.account_email == "signer2@example.com"), None)
    
    if signer_to_remove:
        # Remove a signer
        remove_signer_response = skribble.signature_request.signer.remove(signature_request_id, signer_to_remove.sid)
        print(colored("Signer removed successfully:", "green"))
        print(colored(remove_signer_response, "cyan"))
    else:
        print(colored("Signer to remove not found", "yellow"))

    # Replace signers in a signature request
    new_signers = [
        {
            "account_email": "newsigner1@example.com",
            "signer_identity_data": {
                "email_address": "newsigner1@example.com",
                "first_name": "New",
                "last_name": "Signer1",
                "language": "en"
            }
        },
        {
            "account_email": "newsigner2@example.com",
            "signer_identity_data": {
                "email_address": "newsigner2@example.com",
                "first_name": "New",
                "last_name": "Signer2",
                "language": "en"
            }
        }
    ]

    replace_signers_response = skribble.signature_request.signer.replace(signature_request_id, new_signers)
    print(colored("Signers replaced successfully:", "green"))
    print(colored(replace_signers_response.model_dump(), "cyan"))

    # Get the created signature request
    get_response = skribble.signature_request.get(signature_request_id)
    print(colored("Retrieved signature request:", "green"))
    print(colored(get_response.model_dump(), "cyan"))

    # Add an attachment
    attachment_request = AttachmentRequest(
        filename="example.txt",
        content_type="text/plain",
        content="SGVsbG8gV29ybGQh"  # Base64 encoded "Hello World!"
    )

    attachments = skribble.signature_request.attachment.add(signature_request_id, attachment_request)
    print(colored(f"Added attachment, now have {len(attachments)} attachments", "green"))

    # List attachments
    attachments = skribble.signature_request.attachment.list(signature_request_id)
    print(colored(f"Found {len(attachments)} attachments", "green"))

    # Get attachment content for our example.txt file
    example_attachment = next((a for a in attachments if a.get("filename") == "example.txt"), None)
    if example_attachment:
        # Get the attachment content
        content = skribble.signature_request.attachment.download(signature_request_id, example_attachment.get("attachment_id"))
        print(colored(f"Got attachment content: {content.decode()}", "green"))

        # Delete attachment
        skribble.signature_request.attachment.delete(signature_request_id, example_attachment.get("attachment_id"))
        print(colored(f"Deleted attachment with filename: {example_attachment.get('filename')}", "green"))
    else:
        print(colored("Could not find example.txt attachment", "yellow"))

    # List signature requests
    list_response = skribble.signature_request.list(page_size=10)
    print(colored("Listed signature requests:", "green"))
    print(colored(f"Total number of signature requests: {len(list_response)}", "cyan"))

    # Withdraw the signature request with a message
    withdraw_response = skribble.signature_request.withdraw(signature_request_id, message="Withdrawing for testing purposes")
    print(colored("Withdrawn signature request:", "green"))
    print(colored(withdraw_response, "cyan"))

    # Delete the signature request
    delete_response = skribble.signature_request.delete(signature_request_id)
    print(colored("Deleted signature request:", "green"))
    print(colored(delete_response, "cyan"))

    # Upload a document
    document_content = requests.get("https://pdfobject.com/pdf/sample.pdf").content
    document_data = {
        "title": "Test Document",
        "content_type": "application/pdf",
        "content": base64.b64encode(document_content).decode('utf-8')
    }
    document = skribble.document.add(document_data)
    print(colored("Document added:", "green"))
    print(colored(document.model_dump(), "cyan"))

    # Get document metadata
    document_id = document.id
    document_metadata = skribble.document.get(document_id)
    print(colored("Document metadata:", "green"))
    print(colored(document_metadata.model_dump(), "cyan"))

    # Download document
    document_content = skribble.document.download(document_id)
    print(colored("Downloaded document size:", "green"), colored(len(document_content), "cyan"), colored("bytes", "green"))

    # Get document preview
    try:
        preview_image = skribble.document.preview(document_id, page_id=0, scale=20, max_retries=10, retry_delay=2)
        print(colored("Preview image size:", "green"), colored(len(preview_image), "cyan"), colored("bytes", "green"))
    except SkribbleAPIError as e:
        print(colored(f"Failed to get preview: {str(e)}", "red"))

    # Delete document
    delete_response = skribble.document.delete(document_id)
    print(colored("Document deletion result:", "green"))
    print(colored(delete_response, "cyan"))

    # List all documents with limit
    all_documents = skribble.document.list(limit=5)
    print(colored("All documents (limited to 5):", "green"))
    print(colored(f"Total number of documents: {len(all_documents)}", "cyan"))

    # Create a seal
    seal_content = requests.get("https://pdfobject.com/pdf/sample.pdf").content
    seal_data = {
        "content": base64.b64encode(seal_content).decode('utf-8'),
        "visual_signature": {
            "position": {
                "x": 20,
                "y": 20,
                "width": 260,
                "height": 120,
                "page": "0"
            },
            "image": {
                "content_type": "image/png",
                "content": base64.b64encode(requests.get("https://i.sstatic.net/9vnaY.jpg").content).decode('utf-8')
            }
        }
    }
    seal_response = skribble.seal.create(seal_data)
    print(colored("Seal created successfully:", "green"))
    print(colored(seal_response.model_dump(), "cyan"))

    # Delete the seal document (normal document deletion)
    if seal_response.document_id:
        seal_delete_response = skribble.document.delete(seal_response.document_id)
        print(colored("Seal deletion result:", "green"))
        print(colored(seal_delete_response, "cyan"))
    else:
        print(colored("No document ID available in seal response", "yellow"))

    # Create a seal with a specific seal (Commented out for demo purposes)
    # specific_seal_content = requests.get("https://pdfobject.com/pdf/sample.pdf").content
    # specific_seal_response = skribble.seal.create_specific(
    #     content=base64.b64encode(specific_seal_content).decode('utf-8'),
    #     account_name="ais_company_seal_some_department"
    # )
    # 
    # Delete the seal document (normal document deletion)
    # seal_delete_response = skribble.document.delete(seal_response.document_id)
    # print(colored("Seal deleted successfully:", "green"))
    # print(colored(seal_delete_response.model_dump(), "cyan"))

    # print(colored("Seal created with specific seal successfully:", "green"))
    # print(colored(specific_seal_response.model_dump(), "cyan"))

    print(colored("="*30, "green"))
    print(colored("    All Operations Passed    ", "green", attrs=["bold"]))
    print(colored("="*30, "green"))

except SkribbleAuthError as e:
    print(colored("Authentication error:", "red"), colored(e.message, "yellow"))
except SkribbleValidationError as e:
    print(colored("Validation error:", "red"))
    print(colored(e.message, "yellow"))
except SkribbleAPIError as e:
    print(colored(f"API error (status code {e.status_code}):", "red"), colored(e.message, "yellow"))
except SkribbleOperationError as e:
    print(colored("Operation error:", "red"))
    print(colored(e.message, "yellow"))
    if e.original_error:
        print(colored("Original error:", "red"), colored(str(e.original_error), "yellow"))
except Exception as e:
    print(colored("An unexpected error occurred:", "red"), colored(str(e), "yellow"))