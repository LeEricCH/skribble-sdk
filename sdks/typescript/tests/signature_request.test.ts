import skribble from '../src';
import axios from 'axios';
import { SkribbleAPIError, SkribbleValidationError } from '../src/errors';
import { SignatureRequest, SignatureRequestResponse, SignerRequest, AttachmentRequest } from '../src/types';
import { SkribbleClient } from '../src/client';

jest.mock('axios');
const mockedAxios = jest.mocked(axios);

describe('Signature Request', () => {
  const mockSignerRequest: SignerRequest = {
    account_email: "signer@example.com",
    signer_identity_data: {
      email_address: "signer@example.com",
      first_name: "John",
      last_name: "Doe"
    }
  };

  const mockRequest: SignatureRequest = {
    title: "Test Request",
    message: "Please sign this document",
    content: "base64_encoded_content",
    content_type: "application/pdf",
    signatures: [mockSignerRequest]
  };

  const mockResponseBase: SignatureRequestResponse = {
    id: "d443f2d4-4b2f-e770-fdbe-86ffcb44ed4f",
    title: "Test Request",
    document_id: "doc-123",
    status_overall: "OPEN",
    signatures: [{
      sid: "sig-123",
      account_email: "signer@example.com",
      status_code: "OPEN"
    }],
    owner: "owner@example.com"
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

  describe('create()', () => {
    it('should create a signature request successfully', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockResponseBase });

      const result = await skribble.signature_request.create(mockRequest);

      expect(result).toEqual(mockResponseBase);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: '/signature-requests',
        data: mockRequest,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should throw validation error for missing title', async () => {
      const invalidRequest = { ...mockRequest, title: '' };
      await expect(skribble.signature_request.create(invalidRequest))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should throw validation error for missing signatures', async () => {
      const invalidRequest = { ...mockRequest, signatures: [] };
      await expect(skribble.signature_request.create(invalidRequest))
        .rejects
        .toThrow(SkribbleValidationError);
    });
  });

  describe('get()', () => {
    it('should get a signature request by ID', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockResponseBase });

      const result = await skribble.signature_request.get(mockResponseBase.id);

      expect(result).toEqual(mockResponseBase);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: `/signature-requests/${mockResponseBase.id}`,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should throw validation error for empty ID', async () => {
      await expect(skribble.signature_request.get(''))
        .rejects
        .toThrow(SkribbleValidationError);
    });
  });

  describe('list()', () => {
    it('should list signature requests with pagination', async () => {
      const mockList = [
        mockResponseBase,
        {
          ...mockResponseBase,
          id: "e443g2d4-4b2g-e770-fdbe-86gfcb44ed4g",
          title: "Test Request 2",
          status_overall: "COMPLETED"
        }
      ];
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockList });

      const result = await skribble.signature_request.list({
        page_size: 10,
        page_number: 1
      });

      expect(result).toEqual(mockList);
      expect(result[0].status_overall).toBe("OPEN");
      expect(result[1].status_overall).toBe("COMPLETED");
    });

    it('should handle empty response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });
      const result = await skribble.signature_request.list();
      expect(result).toEqual([]);
    });

    it('should handle filtering by account email', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [mockResponseBase] });
      await skribble.signature_request.list({ account_email: 'test@example.com' });
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'GET',
        url: '/signature-requests',
        params: { account_email: 'test@example.com' },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle non-array response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: null });
      const result = await skribble.signature_request.list();
      expect(result).toEqual([]);
    });
  });

  describe('update()', () => {
    it('should update a signature request', async () => {
      const updateData = {
        title: 'Updated Title',
        message: 'Updated message'
      };
      mockAxiosInstance.request.mockResolvedValueOnce({ data: { ...mockResponseBase, ...updateData } });

      const result = await skribble.signature_request.update(mockResponseBase.id, updateData);

      expect(result.title).toBe(updateData.title);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'PUT',
        url: '/signature-requests',
        data: { id: mockResponseBase.id, ...updateData },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should throw validation error for empty ID', async () => {
      await expect(skribble.signature_request.update('', {}))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should handle API errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { message: 'Invalid update data' }
        }
      });

      await expect(skribble.signature_request.update(mockResponseBase.id, {}))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('withdraw()', () => {
    it('should withdraw a signature request', async () => {
      const withdrawnResponse = { ...mockResponseBase, status_overall: 'WITHDRAWN' };
      mockAxiosInstance.request.mockResolvedValueOnce({ data: withdrawnResponse });

      const result = await skribble.signature_request.withdraw(mockResponseBase.id, 'No longer needed');

      expect(result.status_overall).toBe('WITHDRAWN');
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: `/signature-requests/${mockResponseBase.id}/withdraw`,
        data: { message: 'No longer needed' },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should throw validation error for empty ID', async () => {
      await expect(skribble.signature_request.withdraw(''))
        .rejects
        .toThrow(SkribbleValidationError);
    });
  });

  describe('remind()', () => {
    it('should send a reminder', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: {} });

      await skribble.signature_request.remind(mockResponseBase.id);

      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: `/signature-requests/${mockResponseBase.id}/remind`,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should throw validation error for empty ID', async () => {
      await expect(skribble.signature_request.remind(''))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should handle API errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { message: 'Cannot send reminder' }
        }
      });

      await expect(skribble.signature_request.remind(mockResponseBase.id))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('delete()', () => {
    it('should delete a signature request', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: {} });

      const result = await skribble.signature_request.delete(mockResponseBase.id);

      expect(result).toEqual({
        status: 'success',
        message: `Signature request ${mockResponseBase.id} deleted successfully`
      });
    });

    it('should throw validation error for empty ID', async () => {
      await expect(skribble.signature_request.delete(''))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should handle API errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 404,
          data: { message: 'Signature request not found' }
        }
      });

      await expect(skribble.signature_request.delete(mockResponseBase.id))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('signer operations', () => {
    describe('add()', () => {
      it('should add a signer', async () => {
        const updatedResponse = {
          ...mockResponseBase,
          signatures: [...mockResponseBase.signatures, {
            sid: 'sig-456',
            account_email: mockSignerRequest.account_email,
            status_code: 'OPEN'
          }]
        };
        mockAxiosInstance.request.mockResolvedValueOnce({ data: updatedResponse });

        const result = await skribble.signature_request.signer.add(mockResponseBase.id, mockSignerRequest);

        expect(result.signatures).toHaveLength(2);
        expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
          method: 'POST',
          url: `/signature-requests/${mockResponseBase.id}/signatures`,
          data: mockSignerRequest,
          headers: expect.any(Object),
          responseType: 'json'
        });
      });

      it('should throw validation error for missing required fields', async () => {
        const invalidSigner = { account_email: 'test@example.com' } as SignerRequest;
        await expect(skribble.signature_request.signer.add(mockResponseBase.id, invalidSigner))
          .rejects
          .toThrow(SkribbleValidationError);
      });
    });

    describe('remove()', () => {
      it('should remove a signer', async () => {
        mockAxiosInstance.request.mockResolvedValueOnce({ data: {} });

        const result = await skribble.signature_request.signer.remove(mockResponseBase.id, 'sig-123');

        expect(result).toEqual({
          status: 'success',
          message: `Signer sig-123 removed successfully from signature request ${mockResponseBase.id}`
        });
      });

      it('should throw validation error for missing IDs', async () => {
        await expect(skribble.signature_request.signer.remove('', ''))
          .rejects
          .toThrow(SkribbleValidationError);
      });
    });

    describe('replace()', () => {
      it('should replace all signers', async () => {
        const newSigners = [
          mockSignerRequest,
          { ...mockSignerRequest, account_email: 'signer2@example.com' }
        ];
        const updatedResponse = {
          ...mockResponseBase,
          signatures: newSigners.map((s, i) => ({
            sid: `sig-${i}`,
            account_email: s.account_email,
            status_code: 'OPEN'
          }))
        };
        mockAxiosInstance.request.mockResolvedValueOnce({ data: updatedResponse });

        const result = await skribble.signature_request.signer.replace(mockResponseBase.id, newSigners);

        expect(result.signatures).toHaveLength(2);
        expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
          method: 'PUT',
          url: '/signature-requests',
          data: { id: mockResponseBase.id, signatures: newSigners },
          headers: expect.any(Object),
          responseType: 'json'
        });
      });

      it('should throw validation error for empty signers array', async () => {
        await expect(skribble.signature_request.signer.replace(mockResponseBase.id, []))
          .rejects
          .toThrow(SkribbleValidationError);
      });

      it('should throw validation error for invalid signer data', async () => {
        const invalidSigners = [{ account_email: 'test@example.com' }] as SignerRequest[];
        await expect(skribble.signature_request.signer.replace(mockResponseBase.id, invalidSigners))
          .rejects
          .toThrow(SkribbleValidationError);
      });
    });
  });

  describe('attachment operations', () => {
    const mockAttachment: AttachmentRequest = {
      filename: 'test.pdf',
      content_type: 'application/pdf',
      content: 'base64_content'
    };

    describe('add()', () => {
      it('should add an attachment', async () => {
        const mockResponse = { attachment_id: 'att-123', filename: 'test.pdf' };
        mockAxiosInstance.request.mockResolvedValueOnce({ data: mockResponse });

        const result = await skribble.signature_request.attachment.add(mockResponseBase.id, mockAttachment);

        expect(result).toEqual(mockResponse);
        expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
          method: 'POST',
          url: `/signature-requests/${mockResponseBase.id}/attachments`,
          data: mockAttachment,
          headers: expect.any(Object),
          responseType: 'json'
        });
      });
    });

    describe('download()', () => {
      it('should download an attachment', async () => {
        const mockBuffer = Buffer.from('test content');
        mockAxiosInstance.request.mockResolvedValueOnce({ data: mockBuffer });

        const result = await skribble.signature_request.attachment.download(mockResponseBase.id, 'att-123');

        expect(result).toBeInstanceOf(Blob);
        expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
          method: 'GET',
          url: `/signature-requests/${mockResponseBase.id}/attachments/att-123/content`,
          data: null,
          params: null,
          headers: expect.any(Object),
          responseType: 'arraybuffer'
        });
      });
    });

    describe('delete()', () => {
      it('should delete an attachment', async () => {
        mockAxiosInstance.request.mockResolvedValueOnce({ data: {} });

        await skribble.signature_request.attachment.delete(mockResponseBase.id, 'att-123');

        expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
          method: 'DELETE',
          url: `/signature-requests/${mockResponseBase.id}/attachments/att-123`,
          headers: expect.any(Object),
          responseType: 'json'
        });
      });
    });

    describe('list()', () => {
      it('should list attachments', async () => {
        const mockAttachments = [
          { attachment_id: 'att-123', filename: 'test1.pdf' },
          { attachment_id: 'att-456', filename: 'test2.pdf' }
        ];
        mockAxiosInstance.request.mockResolvedValueOnce({ 
          data: { ...mockResponseBase, attachments: mockAttachments }
        });

        const result = await skribble.signature_request.attachment.list(mockResponseBase.id);

        expect(result).toEqual(mockAttachments);
      });

      it('should handle missing attachments', async () => {
        mockAxiosInstance.request.mockResolvedValueOnce({ 
          data: { ...mockResponseBase, attachments: undefined }
        });

        const result = await skribble.signature_request.attachment.list(mockResponseBase.id);

        expect(result).toEqual([]);
      });
    });
  });
}); 