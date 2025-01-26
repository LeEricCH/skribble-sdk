import { SkribbleClient } from '../client';
import { Document, DocumentRequest, DocumentContent } from '../types';
import { SkribbleValidationError, SkribbleAPIError } from '../errors';

/**
 * List all documents.
 * 
 * @param limit - The maximum number of documents to return. If undefined, returns all documents.
 * @returns A promise that resolves to a list of documents.
 * 
 * @example
 * ```typescript
 * const documents = await skribble.document.list(5);
 * console.log(documents.length);
 * ```
 */
export async function list(limit?: number): Promise<Document[]> {
  const client = SkribbleClient.getInstance();
  const response = await client.makeRequest('GET', '/documents');
  return limit ? response.slice(0, limit) : response;
}

/**
 * Get the document metadata.
 * 
 * @param documentId - The ID of the document to retrieve.
 * @returns A promise that resolves to the document metadata.
 * 
 * @example
 * ```typescript
 * const metadata = await skribble.document.get("5c33d0cb-84...");
 * console.log(metadata.title);
 * ```
 */
export async function get(documentId: string): Promise<Document> {
  const client = SkribbleClient.getInstance();
  const response = await client.makeRequest('GET', `/documents/${documentId}`);
  return response as Document;
}

/**
 * Delete a document.
 * 
 * @param documentId - The ID of the document to delete.
 * @returns A promise that resolves to the status of the delete operation.
 * 
 * @example
 * ```typescript
 * const result = await skribble.document.delete("5c33d0cb-84...");
 * console.log(result.status);
 * ```
 */
export async function deleteDocument(documentId: string): Promise<{ status: string; message: string }> {
  const client = SkribbleClient.getInstance();
  try {
    await client.makeRequest('DELETE', `/documents/${documentId}`);
    return { status: 'success', message: `Document ${documentId} deleted successfully` };
  } catch (error) {
    if (error instanceof SkribbleAPIError) {
      return { status: 'error', message: `Failed to delete document: ${error.message}` };
    }
    throw error;
  }
}

/**
 * Add a new document.
 * 
 * @param documentData - The document data.
 * @returns A promise that resolves to the created document details.
 * 
 * @example
 * ```typescript
 * const documentData = {
 *   title: "New Document",
 *   content_type: "application/pdf",
 *   content: "base64_encoded_pdf_content"
 * };
 * const result = await skribble.document.add(documentData);
 * console.log(result.id);
 * ```
 */
export async function add(documentData: DocumentRequest): Promise<Document> {
  const client = SkribbleClient.getInstance();
  return client.makeRequest('POST', '/documents', documentData);
}

/**
 * Download the document content.
 * 
 * @param documentId - The ID of the document to download.
 * @param contentType - The type of content to return: 'blob' for raw bytes or 'base64' for base64 encoded string.
 * @returns A promise that resolves to either a Blob or a base64 string depending on the contentType parameter.
 * 
 * @example
 * ```typescript
 * // Download as blob
 * const blobContent = await skribble.document.download("5c33d0cb-84...", 'blob');
 * console.log(blobContent.size);
 * 
 * // Download as base64
 * const base64Content = await skribble.document.download("5c33d0cb-84...", 'base64');
 * console.log(base64Content.substring(0, 50));
 * ```
 */
export async function download(
  documentId: string,
  contentType: 'blob' | 'base64' = 'blob'
): Promise<DocumentContent> {
  const client = SkribbleClient.getInstance();
  const headers = contentType === 'base64' ? { Accept: 'application/json' } : undefined;
  const responseType = contentType === 'base64' ? 'json' : 'blob';
  
  const response = await client.makeRequest(
    'GET',
    `/documents/${documentId}/content`,
    null,
    headers,
    responseType
  );

  if (contentType === 'base64') {
    return (response as { content: string }).content;
  }
  
  return response as Blob;
}

/**
 * Get the document page preview with retry mechanism.
 * 
 * @param documentId - The ID of the document.
 * @param pageId - The page number (starting from 0).
 * @param scale - The scale of the preview (20 for thumbnail, 100 for full size).
 * @param maxRetries - Maximum number of retries for polling.
 * @param retryDelay - Delay between retries in milliseconds.
 * @returns A promise that resolves to the preview image content as a Blob.
 * 
 * @example
 * ```typescript
 * const preview = await skribble.document.preview("5c33d0cb-84...", 0, 20);
 * console.log(preview.type);
 * ```
 */
export async function preview(
  documentId: string,
  pageId: number,
  scale: number = 20,
  maxRetries: number = 5,
  retryDelay: number = 2000
): Promise<Blob> {
  const client = SkribbleClient.getInstance();
  const url = `/documents/${documentId}/pages/${pageId}?scale=${scale}`;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await client.makeRequest('GET', url, null, null, 'blob');
      if (response instanceof Blob && response.size > 0) {
        return response;
      }
      // If the response is empty, wait and retry
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    } catch (error) {
      if (error instanceof SkribbleAPIError && error.statusCode === 202) {
        // If the status is 202, it means the preview is still generating
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        continue;
      }
      throw error;
    }
  }

  throw new SkribbleAPIError(`Failed to get document preview after ${maxRetries} attempts`, 500);
}

// Export the function as 'delete'
export { deleteDocument as delete };