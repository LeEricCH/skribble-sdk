import { SkribbleClient } from '../client';
import { SignatureRequest, SignatureRequestResponse, Signature, SignerRequest, AttachmentRequest, AttachmentResponse } from '../types';
import { SkribbleValidationError, SkribbleAPIError } from '../errors';

/**
 * Create a new signature request.
 * 
 * @param signatureRequest - The signature request data.
 * @returns A promise that resolves to the created signature request details.
 * @throws {SkribbleValidationError} If the input data is invalid.
 * 
 * @example
 * ```typescript
 * const request = {
 *   title: "Test Request",
 *   message: "Please sign",
 *   file_url: "https://example.com/document.pdf",
 *   signatures: [{ account_email: "signer@example.com" }]
 * };
 * const result = await skribble.signature_request.create(request);
 * console.log(result.id);
 * ```
 */
export async function create(signatureRequest: SignatureRequest): Promise<SignatureRequestResponse> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('POST', '/signature-requests', signatureRequest);
}

/**
 * Get details of a specific signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to retrieve.
 * @returns A promise that resolves to the signature request details.
 * 
 * @example
 * ```typescript
 * const details = await skribble.signature_request.get("5c33d0cb-84...");
 * console.log(details.title);
 * ```
 */
export async function get(signatureRequestId: string): Promise<SignatureRequestResponse> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('GET', `/signature-requests/${signatureRequestId}`);
}

/**
 * List signature requests with optional filtering and pagination.
 * 
 * @param params - Optional parameters for filtering and pagination.
 * @returns A promise that resolves to a list of signature request details.
 * 
 * @example
 * ```typescript
 * const requests = await skribble.signature_request.list({
 *   account_email: "john.doe@example.com",
 *   search: "Contract",
 *   signature_status: "OPEN",
 *   status_overall: "OPEN",
 *   page_number: 1,
 *   page_size: 10
 * });
 * console.log(requests.length);
 * ```
 */
export async function list(params?: {
  account_email?: string;
  search?: string;
  signature_status?: string;
  status_overall?: string;
  page_number?: number;
  page_size?: number;
}): Promise<SignatureRequestResponse[]> {
  const client = SkribbleClient.getInstance();
  
  const { page_number, page_size, ...apiParams } = params || {};
  
  const allRequests = await client.makeRequest('GET', '/signature-requests', null, apiParams);
  
  const pageNumber = page_number || 0;
  const itemsPerPage = page_size || 50;
  const startIndex = pageNumber * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  
  return allRequests.slice(startIndex, endIndex);
}

/**
 * Update a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to update.
 * @param updatedData - The updated data for the signature request.
 * @returns A promise that resolves to the updated signature request details.
 * 
 * @example
 * ```typescript
 * const updatedRequest = await skribble.signature_request.update("5c33d0cb-84...", {
 *   title: "Updated Title"
 * });
 * console.log(updatedRequest.title);
 * ```
 */
export async function update(signatureRequestId: string, updatedData: Partial<SignatureRequest>): Promise<SignatureRequestResponse> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('PUT', '/signature-requests', { id: signatureRequestId, ...updatedData });
}

/**
 * Withdraw a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to withdraw.
 * @param message - Optional message to include with the withdrawal.
 * @returns A promise that resolves to the updated signature request after withdrawal.
 * 
 * @example
 * ```typescript
 * const result = await skribble.signature_request.withdraw("5c33d0cb-84...", "Request no longer needed");
 * console.log(result.status_overall); // 'WITHDRAWN'
 * ```
 */
export async function withdraw(signatureRequestId: string, message?: string): Promise<SignatureRequestResponse> {
  const client = SkribbleClient.getInstance();
  const response = await client.makeRequest('POST', `/signature-requests/${signatureRequestId}/withdraw`, { message });
  return response;
}

/**
 * Send a reminder for a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to remind.
 * @returns A promise that resolves when the reminder is sent successfully.
 * 
 * @example
 * ```typescript
 * await skribble.signature_request.remind("5c33d0cb-84...");
 * console.log("Reminder sent successfully");
 * ```
 */
export async function remind(signatureRequestId: string): Promise<void> {
  const client = SkribbleClient.getInstance();
  await client.makeRequest('POST', `/signature-requests/${signatureRequestId}/remind`);
}

/**
 * Delete a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to delete.
 * @returns A promise that resolves to the response of the deletion operation.
 * 
 * @example
 * ```typescript
 * const result = await skribble.signature_request.delete("5c33d0cb-84...");
 * console.log(result);
 * ```
 */
export async function deleteSignatureRequest(signatureRequestId: string): Promise<{ status: string; message: string }> {
  const client = SkribbleClient.getInstance();
  await client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}`);
  return { status: 'success', message: `Signature request ${signatureRequestId} deleted successfully` };
}

// Export the function as 'delete'
export { deleteSignatureRequest as delete };

// Signer operations submodule
export const signer = {
  async add(signatureRequestId: string, signerData: SignerRequest): Promise<SignatureRequestResponse> {
    const client = SkribbleClient.getInstance();
    return client.makeRequest('POST', `/signature-requests/${signatureRequestId}/signatures`, signerData);
  },

  async remove(signatureRequestId: string, signerId: string): Promise<{ status: string; message: string }> {
    const client = SkribbleClient.getInstance();
    await client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}/signatures/${signerId}`);
    return { status: 'success', message: `Signer with ID ${signerId} removed successfully` };
  },

  async replace(signatureRequestId: string, signatures: SignerRequest[]): Promise<SignatureRequestResponse> {
    const client = SkribbleClient.getInstance();
    return client.makeRequest('PUT', '/signature-requests', { id: signatureRequestId, signatures });
  }
};

// Attachment operations submodule
export const attachment = {
  async add(signatureRequestId: string, attachment: AttachmentRequest): Promise<AttachmentResponse> {
    const client = SkribbleClient.getInstance();
    const response = await client.makeRequest('POST', `/signature-requests/${signatureRequestId}/attachments`, attachment);
    return response;
  },

  async download(signatureRequestId: string, attachmentId: string): Promise<Blob> {
    const client = SkribbleClient.getInstance();
    return client.makeRequest('GET', `/signature-requests/${signatureRequestId}/attachments/${attachmentId}/content`, null, null, 'blob');
  },

  async delete(signatureRequestId: string, attachmentId: string): Promise<void> {
    const client = SkribbleClient.getInstance();
    await client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}/attachments/${attachmentId}`);
  },

  async list(signatureRequestId: string): Promise<AttachmentResponse> {
    const client = SkribbleClient.getInstance();
    const signatureRequest = await client.makeRequest('GET', `/signature-requests/${signatureRequestId}`);
    return signatureRequest.attachments || [];
  }
};