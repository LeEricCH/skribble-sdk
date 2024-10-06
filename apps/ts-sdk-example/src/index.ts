import skribble, { handleSkribbleError, Types, SkribbleAPIError } from 'skribble-sdk';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

// Replace with your actual API credentials
const USERNAME = 'api_xxx';
const API_KEY = 'xxxxx';

async function fetchPDF(url: string): Promise<Buffer> {
  const response = await axios.get(url, { responseType: 'arraybuffer' });
  return Buffer.from(response.data);
}

async function fetchImage(url: string): Promise<Buffer> {
  const response = await axios.get(url, { responseType: 'arraybuffer' });
  return Buffer.from(response.data);
}

async function main() {
  try {
    // Initialize the SDK with username and API key
    const accessToken = await skribble.init(USERNAME, API_KEY);
    console.log('SDK initialized with access token:', accessToken);

    // Reinitialize the SDK with the access token (not needed, just for demo purposes)
    await skribble.init(accessToken);
    console.log('SDK reinitialized with access token');

    // Create a sample signature request
    const signatureRequest: Types.SignatureRequest = {
      title: "Test Signature Request",
      message: "Please sign this test document",
      file_url: "https://pdfobject.com/pdf/sample.pdf",
      signatures: [
        {
          account_email: "signer1@example.com",
          signer_identity_data: {
            email_address: "signer1@example.com",
            mobile_number: "1234567890",
            first_name: "John",
            last_name: "Doe",
            language: "en"
          },
          sequence: 1,
        },
        {
          account_email: "signer2@example.com",
          signer_identity_data: {
            email_address: "signer2@example.com",
            mobile_number: "0987654321",
            first_name: "Jane",
            last_name: "Smith",
            language: "en"
          },
          sequence: 2,
        },
      ],
    };

    // Create a signature request
    const createResponse = await skribble.signature_request.create(signatureRequest);
    console.log("Signature request created successfully:", createResponse);

    // Remind signer about the signature request
    await skribble.signature_request.remind(createResponse.id);
    console.log("Reminded signer about the signature request");

    const signatureRequestId = createResponse.id;

    // Add signer to the signature request
    const addSignerResponse = await skribble.signature_request.add_signer(createResponse.id, {
      account_email: "test@test.com",
      signer_identity_data: {
        email_address: "test@test.com",
        mobile_number: "1234567890",
        first_name: "Test",
        last_name: "User",
      },
      language: "en"
    });
    console.log("Signer added successfully:", addSignerResponse);

    // Get the created signature request to find the signer ID
    const getResponse = await skribble.signature_request.get(signatureRequestId);
    const signerToRemove = getResponse.signatures.find((signer: Types.Signature) => 
      signer.signer_identity_data?.email_address === "signer2@example.com" ||
      signer.account_email === "signer2@example.com"
    );
    
    if (signerToRemove) {
      // Remove a signer
      const removeSignerResponse = await skribble.signature_request.remove_signer(signatureRequestId, signerToRemove.sid);
      console.log("Signer removed successfully:", removeSignerResponse);
    } else {
      console.log("Signer to remove not found");
    }

    // Replace signers in a signature request
    const newSigners = [
      {
        account_email: "newsigner1@example.com",
        signer_identity_data: {
          email_address: "newsigner1@example.com",
          first_name: "New",
          last_name: "Signer1",
          language: "en"
        }
      },
      {
        account_email: "newsigner2@example.com",
        signer_identity_data: {
          email_address: "newsigner2@example.com",
          first_name: "New",
          last_name: "Signer2",
          language: "en"
        }
      }
    ];

    const replaceSignersResponse = await skribble.signature_request.replace_signers(signatureRequestId, newSigners);
    console.log("Signers replaced successfully:", replaceSignersResponse);

    // Get the updated signature request
    const updatedGetResponse = await skribble.signature_request.get(signatureRequestId);
    console.log("Retrieved signature request:", updatedGetResponse);

    // Add multiple attachments
    const attachmentUrls = [
      "https://pdfobject.com/pdf/sample.pdf",
      "https://pdfobject.com/pdf/sample.pdf"
    ];
    const attachments = await Promise.all(attachmentUrls.map(async (url, index) => {
      const attachmentContent = await fetchPDF(url);
      return {
        filename: `attachment-${index + 1}.pdf`,
        content_type: "application/pdf",
        content: attachmentContent.toString('base64')
      };
    }));
    try {
      const attachmentResponse = await skribble.attachment.add(signatureRequestId, attachments);
      console.log("Attachments added successfully:", attachmentResponse);

      // List attachments
      const attachmentList = await skribble.attachment.list(signatureRequestId);
      console.log("Attachments in the signature request:", attachmentList);
    } catch (error) {
      const skribbleError = handleSkribbleError(error);
      console.error("Failed to add attachments:", skribbleError.message);
      if (skribbleError instanceof SkribbleAPIError) {
        console.error("Status code:", skribbleError.statusCode);
        console.error("Response data:", skribbleError.responseData);
      }
    }

    // Check if there are any attachments and delete all of them
    const latestGetResponse = await skribble.signature_request.get(signatureRequestId);
    if (latestGetResponse.attachments && latestGetResponse.attachments.length > 0) {
      for (const attachment of latestGetResponse.attachments) {
        try {
          await skribble.attachment.deleteAttachment(signatureRequestId, attachment.attachment_id);
          console.log(`Attachment ${attachment.attachment_id} deleted successfully`);
        } catch (error) {
          console.error(`Failed to delete attachment ${attachment.attachment_id}:`, error);
        }
      }

      // Verify all attachments were deleted
      const finalGetResponse = await skribble.signature_request.get(signatureRequestId);
      if (!finalGetResponse.attachments || finalGetResponse.attachments.length === 0) {
        console.log("All attachments deletion confirmed");
      } else {
        console.log("Attachment deletion failed: Some attachments are still present in the signature request");
      }
    } else {
      console.log("No attachments found in the signature request");
    }

    // List signature requests
    const listResponse = await skribble.signature_request.list({ page_size: 10 });
    console.log("Listed signature requests:", listResponse.length);

    // Withdraw the signature request with a message
    const withdrawResponse = await skribble.signature_request.withdraw(signatureRequestId, "Withdrawing for testing purposes");
    console.log("Withdrawn signature request:", withdrawResponse);

    // Delete the signature request
    const deleteResponse = await skribble.signature_request.delete(signatureRequestId);
    console.log("Deleted signature request:", deleteResponse);

    // Upload a document
    const documentContent = await fetchPDF("https://pdfobject.com/pdf/sample.pdf");
    const documentData = {
      title: "Test Document",
      content_type: "application/pdf",
      content: documentContent.toString('base64')
    };
    const document = await skribble.document.add(documentData);
    console.log("Document added:", document);

    // Get document metadata
    const documentId = document.id;
    const documentMetadata = await skribble.document.get(documentId);
    console.log("Document metadata:", documentMetadata);

    // Download document
    const documentContentDownloaded = await skribble.document.download(documentId);
    console.log("Downloaded document size:", documentContentDownloaded.size, "bytes");

    // Get document preview
    try {
      const previewImage = await skribble.document.preview(documentId, 0, 20, 10, 2000);
      console.log("Preview image size:", previewImage.size, "bytes");
    } catch (error) {
      const skribbleError = handleSkribbleError(error);
      console.error("Failed to get preview:", skribbleError.message);
      if (skribbleError instanceof SkribbleAPIError) {
        console.error("Status code:", skribbleError.statusCode);
        console.error("Response data:", skribbleError.responseData);
      }
    }

    // Delete document
    const documentDeleteResponse = await skribble.document.delete(documentId);
    console.log("Document deletion result:", documentDeleteResponse);

    // List all documents with limit
    const allDocuments = await skribble.document.list(5);
    console.log("All documents (limited to 5):", allDocuments.length);

    // Create a seal
    const sealContent = await fetchPDF("https://pdfobject.com/pdf/sample.pdf");
    const sealImage = await fetchImage("https://i.stack.imgur.com/9vnaY.jpg");
    const sealData = {
      content: sealContent.toString('base64'),
      visual_signature: {
        position: {
          x: 20,
          y: 20,
          width: 260,
          height: 120,
          page: "0"
        },
        image: {
          content_type: "image/png",
          content: sealImage.toString('base64')
        }
      }
    };
    const sealResponse = await skribble.seal.create(sealData);
    console.log("Seal created successfully:", sealResponse);

    // Delete the seal document (normal document deletion)
    const sealId = sealResponse.document_id;
    const sealDeleteResponse = await skribble.document.delete(sealId);
    console.log("Seal deletion result:", sealDeleteResponse);

    console.log("========================================");
    console.log("    All Operations Passed");
    console.log("========================================");

  } catch (error) {
    const skribbleError = handleSkribbleError(error);
    console.error("An Skribble error occurred:", skribbleError.message);
    if (skribbleError instanceof SkribbleAPIError) {
      console.error("Status code:", skribbleError.statusCode);
      console.error("Response data:", skribbleError.responseData);
    }
  }
}

main();