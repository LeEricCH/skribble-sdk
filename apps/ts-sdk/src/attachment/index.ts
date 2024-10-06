import { SkribbleClient } from '../client';
import { Attachment } from '../types';
import { SkribbleValidationError, SkribbleAPIError } from '../errors';

/**
 * Add multiple attachments to a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param attachments - An array of attachment information.
 * @returns A promise that resolves to an array of added attachment IDs and filenames.
 * @throws {SkribbleValidationError} If the input data is invalid.
 * @throws {SkribbleAPIError} If the API request fails.
 * 
 * @example
 * ```typescript
 * const attachments = [
 *   { filename: "doc1.pdf", content_type: "application/pdf", content: "base64_content" },
 *   { filename: "doc2.pdf", content_type: "application/pdf", content: "base64_content" }
 * ];
 * const result = await skribble.attachment.add("5c33d0cb-84...", attachments);
 * console.log(result);
 * ```
 */
export async function add(signatureRequestId: string, attachments: Attachment[]): Promise<{ attachment_id: string, filename: string }[]> {
  const client = SkribbleClient.getInstance();
  let finalResponse;

  for (const attachment of attachments) {
    finalResponse = await client.makeRequest('POST', `/signature-requests/${signatureRequestId}/attachments`, attachment);
  }

  // Return only the attachments from the final response
  return finalResponse?.attachments || [];
}
    
/**
 * Download a specific attached file from a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param attachmentId - The ID of the attachment to download.
 * @returns A promise that resolves to the content of the attachment file as a Blob.
 * 
 * @example
 * ```typescript
 * const content = await skribble.attachment.get("5c33d0cb-84...", "att_1");
 * console.log(content.size);
 * ```
 */
export async function get(signatureRequestId: string, attachmentId: string): Promise<Blob> {
  const client = SkribbleClient.getInstance();
  const response = await client.makeRequest('GET', `/signature-requests/${signatureRequestId}/attachments/${attachmentId}/content`, null, null, 'blob');
  return response as Blob;
}

/**
 * Remove an attachment from a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param attachmentId - The ID of the attachment to remove.
 * @returns A promise that resolves when the attachment is successfully deleted.
 * @throws {SkribbleAPIError} If the deletion fails.
 * 
 * @example
 * ```typescript
 * await skribble.attachment.delete("5c33d0cb-84...", "att_1");
 * console.log("Attachment deleted successfully");
 * ```
 */
export async function deleteAttachment(signatureRequestId: string, attachmentId: string): Promise<void> {
  const client = SkribbleClient.getInstance();
  await client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}/attachments/${attachmentId}`);
}

/**
 * List all attachments for a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @returns A promise that resolves to an array of attachment information.
 * @throws {SkribbleAPIError} If the API request fails.
 * 
 * @example
 * ```typescript
 * const attachments = await skribble.attachment.list("5c33d0cb-84...");
 * console.log(attachments);
 * ```
 */
export async function list(signatureRequestId: string): Promise<{ attachment_id: string, filename: string }[]> {
  const client = SkribbleClient.getInstance();
  const signatureRequest = await client.makeRequest('GET', `/signature-requests/${signatureRequestId}`);
  return signatureRequest.attachments || [];
}