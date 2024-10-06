import { SkribbleClient } from '../client';
import { SignatureRequest, Signature } from '../types';
import { SkribbleValidationError } from '../errors';

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
export async function create(signatureRequest: SignatureRequest): Promise<any> {
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
export async function get(signatureRequestId: string): Promise<any> {
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
}): Promise<any[]> {
  const client = SkribbleClient.getInstance();
  
  // Remove page_number and page_size from the params sent to the API
  const { page_number, page_size, ...apiParams } = params || {};
  
  // Fetch all results from the API
  const allRequests = await client.makeRequest('GET', '/signature-requests', null, apiParams);
  
  // Apply client-side pagination
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
export async function update(signatureRequestId: string, updatedData: Partial<SignatureRequest>): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('PUT', '/signature-requests', { id: signatureRequestId, ...updatedData });
}

/**
 * Add a signer to a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param signerData - The signer data including email, name, etc.
 * @returns A promise that resolves to the response containing the added signer details.
 * @throws {SkribbleOperationError} If the operation fails.
 * 
 * @example
 * ```typescript
 * const signerData = {
 *   account_email: "new_signer@example.com",
 *   signer_identity_data: {
 *     email_address: "new_signer@example.com",
 *     first_name: "John",
 *     last_name: "Doe"
 *   }
 * };
 * const result = await skribble.signature_request.add_signer("5c33d0cb-84...", signerData);
 * console.log(result.sid);
 * ```
 */
export async function add_signer(signatureRequestId: string, signerData: Signature): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('POST', `/signature-requests/${signatureRequestId}/signatures`, signerData);
}

/**
 * Remove a signer from a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param signerId - The ID of the signer to remove.
 * @returns A promise that resolves to the response of the removal operation.
 * 
 * @example
 * ```typescript
 * const result = await skribble.signature_request.remove_signer("5c33d0cb-84...", "signer123");
 * console.log(result);
 * ```
 */
export async function remove_signer(signatureRequestId: string, signerId: string): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}/signatures/${signerId}`);
}

/**
 * Replace all signers in a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request.
 * @param signatures - An array of new signer data to replace existing signers.
 * @returns A promise that resolves to the updated signature request details.
 * 
 * @example
 * ```typescript
 * const newSigners = [
 *   { account_email: "signer1@example.com" },
 *   { account_email: "signer2@example.com" }
 * ];
 * const result = await skribble.signature_request.replace_signers("5c33d0cb-84...", newSigners);
 * console.log(result);
 * ```
 */
export async function replace_signers(signatureRequestId: string, signatures: Signature[]): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('PUT', '/signature-requests', { id: signatureRequestId, signatures });
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
 * Withdraw a signature request.
 * 
 * @param signatureRequestId - The ID of the signature request to withdraw.
 * @param message - Optional message to include with the withdrawal.
 * @returns A promise that resolves to the response of the withdrawal operation.
 * 
 * @example
 * ```typescript
 * const result = await skribble.signature_request.withdraw("5c33d0cb-84...", "Request no longer needed");
 * console.log(result);
 * ```
 */
export async function withdraw(signatureRequestId: string, message?: string): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('POST', `/signature-requests/${signatureRequestId}/withdraw`, { message });
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
export async function deleteSignatureRequest(signatureRequestId: string): Promise<any> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}`);
}

// Export the function as 'delete'
export { deleteSignatureRequest as delete };