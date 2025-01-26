import { SkribbleClient } from '../client';
import { SignatureRequest, SignatureRequestResponse, Signature, SignerRequest, AttachmentRequest, AttachmentResponse } from '../types';
import { SkribbleValidationError, SkribbleAPIError } from '../errors';

interface ListOptions {
  account_email?: string;
  search?: string;
  signature_status?: string;
  status_overall?: string;
  page_number?: number;
  page_size?: number;
}

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
export async function create(request: SignatureRequest): Promise<SignatureRequestResponse> {
  if (!request.title || !request.signatures || request.signatures.length === 0) {
    throw new SkribbleValidationError('Invalid signature request data', [
      { field: 'title', msg: 'Title is required' },
      { field: 'signatures', msg: 'At least one signature is required' }
    ]);
  }
  const client = SkribbleClient.getInstance();
  return client.makeRequest('POST', '/signature-requests', request);
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
  if (!signatureRequestId) {
    throw new SkribbleValidationError('Signature request ID is required');
  }
  const client = SkribbleClient.getInstance();
  return client.makeRequest('GET', `/signature-requests/${signatureRequestId}`);
}

/**
 * List signature requests with optional filtering and pagination.
 * 
 * @param options - Optional parameters for filtering and pagination.
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
export async function list(options?: ListOptions): Promise<SignatureRequestResponse[]> {
  const client = SkribbleClient.getInstance();
  const response = await client.makeRequest('GET', '/signature-requests', undefined, options);
  return Array.isArray(response) ? response : [];
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
export async function update(id: string, updateData: Partial<SignatureRequest>): Promise<SignatureRequestResponse> {
  if (!id) {
    throw new SkribbleValidationError('Signature request ID is required');
  }

  const client = SkribbleClient.getInstance();
  try {
    const response = await client.makeRequest('PUT', '/signature-requests', {
      id,
      ...updateData
    });
    return response;
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw error;
    }
    throw new SkribbleAPIError('Failed to update signature request', 500);
  }
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
export async function withdraw(id: string, message?: string): Promise<SignatureRequestResponse> {
  if (!id) {
    throw new SkribbleValidationError('Signature request ID is required');
  }

  const client = SkribbleClient.getInstance();
  try {
    const response = await client.makeRequest('POST', `/signature-requests/${id}/withdraw`, {
      message
    });
    return response;
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw error;
    }
    throw new SkribbleAPIError('Failed to withdraw signature request', 500);
  }
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
export async function remind(id: string): Promise<void> {
  if (!id) {
    throw new SkribbleValidationError('Signature request ID is required');
  }

  const client = SkribbleClient.getInstance();
  try {
    await client.makeRequest('POST', `/signature-requests/${id}/remind`);
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw error;
    }
    throw new SkribbleAPIError('Failed to send reminder', 500);
  }
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
export async function deleteSignatureRequest(id: string): Promise<{ status: string; message: string }> {
  if (!id) {
    throw new SkribbleValidationError('Signature request ID is required');
  }

  const client = SkribbleClient.getInstance();
  try {
    await client.makeRequest('DELETE', `/signature-requests/${id}`);
    return {
      status: 'success',
      message: `Signature request ${id} deleted successfully`
    };
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw error;
    }
    throw new SkribbleAPIError('Failed to delete signature request', 500);
  }
}

// Export the function as 'delete'
export { deleteSignatureRequest as delete };

// Signer operations submodule
export const signer = {
  /**
   * Add a new signer to a signature request.
   * 
   * @param signatureRequestId - The ID of the signature request.
   * @param signer - The signer data.
   * @returns A promise that resolves to the updated signature request.
   */
  async add(signatureRequestId: string, signer: SignerRequest): Promise<SignatureRequestResponse> {
    if (!signatureRequestId) {
      throw new SkribbleValidationError('Signature request ID is required');
    }
    if (!signer.account_email || !signer.signer_identity_data) {
      throw new SkribbleValidationError('Invalid signer data', [
        { field: 'account_email', msg: 'Account email is required' },
        { field: 'signer_identity_data', msg: 'Signer identity data is required' }
      ]);
    }
    const client = SkribbleClient.getInstance();
    return client.makeRequest('POST', `/signature-requests/${signatureRequestId}/signatures`, signer);
  },

  /**
   * Remove a signer from a signature request.
   * 
   * @param signatureRequestId - The ID of the signature request.
   * @param signerId - The ID of the signer to remove.
   * @returns A promise that resolves when the signer is removed.
   */
  async remove(signatureRequestId: string, signerId: string): Promise<{ status: string; message: string }> {
    if (!signatureRequestId || !signerId) {
      throw new SkribbleValidationError('Both signature request ID and signer ID are required');
    }
    const client = SkribbleClient.getInstance();
    await client.makeRequest('DELETE', `/signature-requests/${signatureRequestId}/signatures/${signerId}`);
    return {
      status: 'success',
      message: `Signer ${signerId} removed successfully from signature request ${signatureRequestId}`
    };
  },

  /**
   * Replace all signers in a signature request.
   * 
   * @param signatureRequestId - The ID of the signature request.
   * @param signers - The new signers data.
   * @returns A promise that resolves to the updated signature request.
   */
  async replace(signatureRequestId: string, signers: SignerRequest[]): Promise<SignatureRequestResponse> {
    if (!signatureRequestId) {
      throw new SkribbleValidationError('Signature request ID is required');
    }
    if (!Array.isArray(signers) || signers.length === 0) {
      throw new SkribbleValidationError('At least one signer is required');
    }
    for (const signer of signers) {
      if (!signer.account_email || !signer.signer_identity_data) {
        throw new SkribbleValidationError('Invalid signer data', [
          { field: 'account_email', msg: 'Account email is required' },
          { field: 'signer_identity_data', msg: 'Signer identity data is required' }
        ]);
      }
    }
    const client = SkribbleClient.getInstance();
    return client.makeRequest('PUT', '/signature-requests', { id: signatureRequestId, signatures: signers });
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