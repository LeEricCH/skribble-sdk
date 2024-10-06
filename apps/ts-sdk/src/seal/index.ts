import { SkribbleClient } from '../client';
import { Seal } from '../types';
import { SkribbleValidationError, SkribbleAPIError } from '../errors';

/**
 * Create a seal for a document.
 * 
 * @param sealData - The seal data.
 * @returns A promise that resolves to the created seal details.
 * @throws {SkribbleValidationError} If the input data is invalid.
 * 
 * @example
 * ```typescript
 * const sealData = {
 *   content: "base64_encoded_pdf_content",
 *   visual_signature: {
 *     position: { x: 20, y: 20, width: 260, height: 120, page: "0" },
 *     image: { content_type: "image/png", content: "base64_encoded_image_content" }
 *   }
 * };
 * const result = await skribble.seal.create(sealData);
 * console.log(result.document_id);
 * ```
 */
export async function create(sealData: Seal): Promise<{ document_id: string; status: string }> {
  const client = SkribbleClient.getInstance();
  try {
    return client.makeRequest('POST', '/seal', sealData);
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw new SkribbleAPIError(`Failed to create seal: ${error.message}`, error.statusCode);
    }
    throw error;
  }
}

/**
 * Create a seal for a document with a specific seal.
 * 
 * @param content - Base64 encoded PDF file.
 * @param accountName - The name of the account Skribble set up for your organization seal.
 * @returns A promise that resolves to the created seal details.
 * @throws {SkribbleValidationError} If the input data is invalid.
 * 
 * @example
 * ```typescript
 * const content = "base64_encoded_pdf_content";
 * const accountName = "company_seal_department_a";
 * const result = await skribble.seal.createSpecific(content, accountName);
 * console.log(result.document_id);
 * ```
 */
export async function createSpecific(content: string, accountName?: string): Promise<{ document_id: string; status: string }> {
  const sealData: Seal = {
    content,
    account_name: accountName
  };

  const client = SkribbleClient.getInstance();
  try {
    return client.makeRequest('POST', '/seal', sealData);
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      throw new SkribbleAPIError(`Failed to create specific seal: ${error.message}`, error.statusCode);
    }
    throw error;
  }
}