import skribble from '../src';
import axios from 'axios';
import { SkribbleAPIError, SkribbleValidationError } from '../src/errors';
import { Seal } from '../src/types';
import { SkribbleClient } from '../src/client';

jest.mock('axios');
const mockedAxios = jest.mocked(axios);

describe('Seal', () => {
  const mockSeal: Seal = {
    title: "Test Seal",
    content: "base64_encoded_content",
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
        content: "base64_encoded_image"
      }
    }
  };

  const mockSealResponse = {
    document_id: "seal-123",
    status: "success"
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
    it('should create a seal successfully', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockSealResponse });

      const result = await skribble.seal.create(mockSeal);

      expect(result).toEqual(mockSealResponse);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: '/seal',
        data: mockSeal,
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle API errors when creating seal', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { message: 'Invalid seal data' }
        }
      });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle network errors when creating seal', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new Error('Network Error'));

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should throw SkribbleValidationError for missing content', async () => {
      const invalidSealData = {
        title: 'Test Seal'
      };

      await expect(skribble.seal.create(invalidSealData as any))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should handle unknown errors when creating seal', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce('unexpected error');

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle null seal data', async () => {
      await expect(skribble.seal.create(null as any))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should handle malformed response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: { invalid: 'response' } });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle empty response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: null });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('createSpecific()', () => {
    const content = "base64_encoded_content";
    const accountName = "company_seal";

    it('should create a specific seal successfully', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockSealResponse });

      const result = await skribble.seal.createSpecific(content, accountName);

      expect(result).toEqual(mockSealResponse);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: '/seal',
        data: {
          content,
          account_name: accountName
        },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should create a specific seal without account name', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockSealResponse });

      const result = await skribble.seal.createSpecific(content);

      expect(result).toEqual(mockSealResponse);
      expect(mockAxiosInstance.request).toHaveBeenLastCalledWith({
        method: 'POST',
        url: '/seal',
        data: {
          content,
          account_name: undefined
        },
        headers: expect.any(Object),
        responseType: 'json'
      });
    });

    it('should handle API errors when creating specific seal', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { message: 'Invalid content' }
        }
      });

      await expect(skribble.seal.createSpecific(content, accountName))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should throw SkribbleValidationError for empty content', async () => {
      await expect(skribble.seal.createSpecific('', 'test-account'))
        .rejects
        .toThrow(SkribbleValidationError);
    });

    it('should throw SkribbleAPIError for invalid account', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 404,
          data: { message: 'Seal account not found' }
        }
      });

      await expect(skribble.seal.createSpecific('base64_content', 'invalid-account'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should throw SkribbleAPIError for rate limiting', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 429,
          data: { message: 'Too many requests' }
        }
      });

      await expect(skribble.seal.createSpecific('base64_content', 'test-account'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle network errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new Error('Network Error'));

      await expect(skribble.seal.createSpecific(content, accountName))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle unknown errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce('unexpected error');

      await expect(skribble.seal.createSpecific(content, accountName))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle malformed response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: { invalid: 'response' } });

      await expect(skribble.seal.createSpecific(content, accountName))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle empty response', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: null });

      await expect(skribble.seal.createSpecific(content, accountName))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });

  describe('error handling', () => {
    it('should handle rate limiting', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 429,
          data: { message: 'Too many requests' }
        }
      });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle server errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle malformed response data', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: null });

      await expect(skribble.seal.create(mockSeal))
        .rejects
        .toThrow(SkribbleAPIError);
    });
  });
}); 