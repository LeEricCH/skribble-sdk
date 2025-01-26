import skribble from '../src';
import axios from 'axios';
import { SkribbleAPIError, SkribbleValidationError } from '../src/errors';
import { Document, DocumentRequest } from '../src/types';
import { SkribbleClient } from '../src/client';

jest.mock('axios');
const mockedAxios = jest.mocked(axios);

describe('Document', () => {
  const mockDocument: Document = {
    id: "doc-123",
    title: "Test Document",
    content_type: "application/pdf",
    size: 1024,
    page_count: 2,
    page_width: 595,
    page_height: 842,
    owner: "test@example.com"
  };

  const mockDocumentRequest: DocumentRequest = {
    title: "New Document",
    content_type: "application/pdf",
    content: "base64_encoded_content"
  };

  let mockAxiosInstance: jest.Mocked<typeof axios>;

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset the singleton instance before each test
    (SkribbleClient as any).instance = null;
    
    // Setup default axios mock
    mockAxiosInstance = {
      request: jest.fn(),
      post: jest.fn(),
      get: jest.fn(),
      delete: jest.fn(),
      create: jest.fn()
    } as any;

    mockedAxios.create.mockReturnValue(mockAxiosInstance);

    // Mock successful authentication
    mockAxiosInstance.request.mockResolvedValueOnce({ data: [] }); // For token validation
    skribble.init('test_token');
  });

  describe('list()', () => {
    it('should list all documents without limit', async () => {
      const mockDocuments = [mockDocument, { ...mockDocument, id: 'doc-456' }];
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockDocuments });

      const result = await skribble.document.list();

      expect(result).toEqual(mockDocuments);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: '/documents',
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should list documents with limit', async () => {
      const mockDocuments = [mockDocument, { ...mockDocument, id: 'doc-456' }];
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockDocuments });

      const result = await skribble.document.list(1);

      expect(result).toHaveLength(1);
      expect(result[0]).toEqual(mockDocument);
    });

    it('should handle empty response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });
      const result = await skribble.document.list();
      expect(result).toEqual([]);
    });
  });

  describe('get()', () => {
    it('should get document metadata', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockDocument });

      const result = await skribble.document.get(mockDocument.id);

      expect(result).toEqual(mockDocument);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: `/documents/${mockDocument.id}`,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle not found error', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { message: 'Document not found' }
        }
      });

      await expect(skribble.document.get('invalid-id'))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('add()', () => {
    it('should add a new document', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockDocument });

      const result = await skribble.document.add(mockDocumentRequest);

      expect(result).toEqual(mockDocument);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: '/documents',
        data: mockDocumentRequest,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle validation errors', async () => {
      const invalidRequest = {} as DocumentRequest;
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { message: 'Invalid document data' }
        }
      });

      await expect(skribble.document.add(invalidRequest))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('delete()', () => {
    it('should delete a document', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: {} });

      const result = await skribble.document.delete(mockDocument.id);

      expect(result).toEqual({
        status: 'success',
        message: `Document ${mockDocument.id} deleted successfully`
      });
    });

    it('should handle delete errors gracefully', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { message: 'Document not found' }
        }
      });

      const result = await skribble.document.delete('invalid-id');
      expect(result.status).toBe('error');
      expect(result.message).toContain('Failed to delete document');
    });
  });

  describe('download()', () => {
    it('should download document as blob', async () => {
      const mockBlob = new Blob(['test content'], { type: 'application/pdf' });
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockBlob });

      const result = await skribble.document.download(mockDocument.id);

      expect(result).toBeInstanceOf(Blob);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: `/documents/${mockDocument.id}/content`,
        data: null,
        params: undefined,
        headers: expect.any(Object),
        responseType: 'arraybuffer'
      });
    });

    it('should download document as base64', async () => {
      const mockBase64 = { content: 'base64_content' };
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockBase64 });

      const result = await skribble.document.download(mockDocument.id, 'base64');

      expect(result).toBe(mockBase64.content);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: `/documents/${mockDocument.id}/content`,
        data: null,
        params: { Accept: 'application/json' },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle download errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { message: 'Document not found' }
        }
      });

      await expect(skribble.document.download('invalid-id'))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new Error('Network Error'));

      await expect(skribble.document.get(mockDocument.id))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle rate limiting', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 429,
          data: { message: 'Too many requests' }
        }
      });

      await expect(skribble.document.get(mockDocument.id))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle server errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      });

      await expect(skribble.document.get(mockDocument.id))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('preview()', () => {
    beforeEach(() => {
      // Clear any previous token validation mocks
      mockAxiosInstance.request.mockReset();
    });

    it('should get document preview successfully', async () => {
      const mockBuffer = Buffer.from('test');
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockBuffer });

      const result = await skribble.document.preview('doc-123', 0);
      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'GET',
        url: '/documents/doc-123/pages/0?scale=20',
        data: null,
        params: null,
        responseType: 'arraybuffer',
        headers: expect.any(Object)
      });
      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
    });

    it('should retry on empty response', async () => {
      const emptyBuffer = Buffer.from('');
      const mockBuffer = Buffer.from('test');
      mockAxiosInstance.request
        .mockResolvedValueOnce({ data: emptyBuffer })
        .mockResolvedValueOnce({ data: mockBuffer });

      const result = await skribble.document.preview('doc-123', 0, 20, 2, 100);
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);
      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
    });

    it('should retry on 202 status', async () => {
      const mockBuffer = Buffer.from('test');
      const axiosError = {
        isAxiosError: true,
        name: 'AxiosError',
        message: 'Request failed with status code 202',
        response: { 
          status: 202, 
          data: { message: 'Still generating' },
          statusText: 'Accepted'
        }
      };
      mockAxiosInstance.request
        .mockRejectedValueOnce(axiosError)
        .mockResolvedValueOnce({ data: mockBuffer });

      const result = await skribble.document.preview('doc-123', 0, 20, 2, 100);
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);
      expect(result).toBeInstanceOf(Blob);
      expect(result.size).toBeGreaterThan(0);
    });

    it('should throw after max retries', async () => {
      const emptyBuffer = Buffer.from('');
      mockAxiosInstance.request
        .mockResolvedValueOnce({ data: emptyBuffer })
        .mockResolvedValueOnce({ data: emptyBuffer });

      await expect(skribble.document.preview('doc-123', 0, 20, 2, 100))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should throw on non-202 API error', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        response: { 
          status: 404, 
          data: { message: 'Not found' },
          statusText: 'Not Found'
        }
      });

      await expect(skribble.document.preview('doc-123', 0))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });
}); 