import skribble
from skribble import SignatureRequest, SkribbleAuthError, SkribbleAPIError, SkribbleValidationError, SkribbleOperationError
import requests
import base64
from termcolor import colored

# Replace with your actual API credentials
USERNAME: str = "api_demo_testing_6067_0"
API_KEY: str = "y7evSdH58hwtGf2mgWBTqJupac3r9xjCERA6QXFKzZ4sNb"

try:
    # Initialize the SDK with username and API key
    skribble.init(username=USERNAME, api_key=API_KEY)

    # Login to the API and get access token
    access_token = skribble.auth.login()
    print(colored("Access token:", "green"))
    print(colored(access_token, "cyan"))

    # Reinitialize the SDK with the access token
    skribble.init(access_token=access_token)

    # Create a sample signature request
    signature_request = {
        "title": "Test Signature Request",
        "message": "Please sign this test document",
        "file_url": "https://pdfobject.com/pdf/sample.pdf",
        "attachments": [
            {
                "file_url": "https://pdfobject.com/pdf/sample.pdf",
                "file_name": "sample.pdf"
            }
        ],
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
    print(colored(create_response, "cyan"))

    # Remind signer about the signature request
    skribble.signature_request.remind(create_response['id'])
    print(colored("Reminded signer about the signature request", "green"))

    signature_request_id = create_response['id']

    # Add a new signer
    new_signer_email = "newsigner@example.com"
    add_signer_response = skribble.signature_request.add_signer(
        signature_request_id,
        email=new_signer_email,
        first_name="New",
        last_name="Signer",
        mobile_number="1234567890",
        language="en"
    )
    print(colored("New signer added successfully:", "green"))
    print(colored(add_signer_response, "cyan"))

    # Get the created signature request to find the signer ID
    get_response = skribble.signature_request.get(signature_request_id)
    signer_to_remove = next((signer for signer in get_response['signatures'] 
                             if signer.get('signer_identity_data', {}).get('email_address') == "signer2@example.com" or
                             signer.get('account_email') == "signer2@example.com"), None)
    
    if signer_to_remove:
        # Remove a signer
        remove_signer_response = skribble.signature_request.remove_signer(signature_request_id, signer_to_remove['sid'])
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

    replace_signers_response = skribble.signature_request.replace_signers(signature_request_id, new_signers)
    print(colored("Signers replaced successfully:", "green"))
    print(colored(replace_signers_response, "cyan"))


    # Get the created signature request
    get_response = skribble.signature_request.get(signature_request_id)
    print(colored("Retrieved signature request:", "green"))
    print(colored(get_response, "cyan"))
    # Add multiple attachments
    attachment_urls = [
        "https://pdfobject.com/pdf/sample.pdf",
        "https://pdfobject.com/pdf/sample.pdf"
    ]
    attachments = []
    for index, url in enumerate(attachment_urls):
        attachment_content = requests.get(url).content
        attachments.append({
            "filename": f"attachment-{index + 1}.pdf",
            "content_type": "application/pdf",
            "content": base64.b64encode(attachment_content).decode('utf-8')
        })
    attachment_response = skribble.attachment.add(signature_request_id, attachments)
    print(colored("Attachments added successfully:", "green"))
    print(colored(attachment_response, "cyan"))

    # Check if there are any attachments and delete all of them
    get_response = skribble.signature_request.get(signature_request_id)
    if 'attachments' in get_response and get_response['attachments']:
        for attachment in get_response['attachments']:
            attachment_id = attachment['attachment_id']
            try:
                # Delete the attachment
                skribble.attachment.delete(signature_request_id, attachment_id)
                print(colored(f"Attachment {attachment_id} deleted successfully", "green"))
            except SkribbleAPIError as e:
                print(colored(f"Failed to delete attachment {attachment_id}: {str(e)}", "red"))

        # Verify all attachments were deleted
        get_response = skribble.signature_request.get(signature_request_id)
        if not get_response['attachments']:
            print(colored("All attachments deletion confirmed", "green"))
        else:
            print(colored("Attachment deletion failed: Some attachments are still present in the signature request", "red"))
    else:
        print(colored("No attachments found in the signature request", "yellow"))

    # List signature requests
    list_response = skribble.signature_request.list(limit=5)
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
    print(colored(document, "cyan"))

    # Get document metadata
    document_id = document['id']
    document_metadata = skribble.document.get(document_id)
    print(colored("Document metadata:", "green"))
    print(colored(document_metadata, "cyan"))

    # Download document
    document_content = skribble.document.download(document_id)
    print(colored("Downloaded document size:", "green"), colored(len(document_content), "cyan"), colored("bytes", "green"))

    # Get document preview
    preview_image = skribble.document.preview(document_id, page_id=0, scale=20)
    print(colored("Preview image size:", "green"), colored(len(preview_image), "cyan"), colored("bytes", "green"))

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
    print(colored(seal_response, "cyan"))

    # Delete the seal document (normal document deletion)
    seal_id = seal_response['document_id']
    seal_delete_response = skribble.document.delete(seal_id)
    print(colored("Seal deletion result:", "green"))
    print(colored(seal_delete_response, "cyan"))

    # Create a seal with a specific seal (Commented out for demo purposes)
    # specific_seal_content = requests.get("https://pdfobject.com/pdf/sample.pdf").content
    # specific_seal_response = skribble.seal.create_specific(
    #     content=base64.b64encode(specific_seal_content).decode('utf-8'),
    #     account_name="ais_company_seal_some_department"
    # )
    # 
    # Delete the seal document (normal document deletion)
    # seal_delete_response = skribble.document.delete(seal_response['document_id'])
    # print(colored("Seal deleted successfully:", "green"))
    # print(colored(seal_delete_response, "cyan"))

    # print(colored("Seal created with specific seal successfully:", "green"))
    # print(colored(specific_seal_response, "cyan"))


    print(colored("="*30, "green"))
    print(colored("    All Operations Passed    ", "green", attrs=["bold"]))
    print(colored("="*30, "green"))

except SkribbleValidationError as e:
    print(colored(f"Validation error: {str(e)}", "red"))
    for error in e.errors:
        print(colored(f"  - {error}", "red"))
except SkribbleAuthError as e:
    print(colored(f"Authentication error: {str(e)}", "red"))
except SkribbleAPIError as e:
    print(colored(f"API error: {str(e)}", "red"))
except SkribbleOperationError as e:
    print(colored(f"Operation '{e.operation}' failed: {e.message}", "red"))
    if e.original_error:
        print(colored(f"Original error: {str(e.original_error)}", "red"))
except Exception as e:
    print(colored(f"An unexpected error occurred: {str(e)}", "red"))
    import traceback
    traceback.print_exc()