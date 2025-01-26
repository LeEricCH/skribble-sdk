import skribble from '../src';
import axios from 'axios';
import { SkribbleAuthError, SkribbleAPIError } from '../src/errors';
import { SkribbleClient } from '../src/client';

jest.mock('axios');
const mockedAxios = jest.mocked(axios);

describe('Authentication', () => {
  const mockCredentials = {
    username: 'test_user',
    api_key: 'test_api_key',
    access_token: 'test_access_token'
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
      create: jest.fn()
    } as any;

    mockedAxios.create.mockReturnValue(mockAxiosInstance);
  });

  describe('init()', () => {
    it('should initialize with username and api key', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce({ 
        data: mockCredentials.access_token 
      });
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });

      const accessToken = await skribble.init(mockCredentials.username, mockCredentials.api_key);
      
      expect(accessToken).toBe(mockCredentials.access_token);
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/access/login',
        { username: mockCredentials.username, "api-key": mockCredentials.api_key }
      );
    });

    it('should initialize with access token', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });

      const accessToken = await skribble.init(mockCredentials.access_token);
      
      expect(accessToken).toBe(mockCredentials.access_token);
      expect(mockAxiosInstance.post).not.toHaveBeenCalled();
    });

    it('should throw SkribbleAuthError on failed authentication', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 401,
          data: { message: 'Invalid credentials' }
        }
      });

      await expect(skribble.init('wrong_user', 'wrong_key'))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should throw error if no credentials provided', async () => {
      await expect(skribble.init(''))
        .rejects
        .toThrow('No authentication credentials provided');
    });

    it('should handle network errors during authentication', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce(new Error('Network Error'));

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle server errors during authentication', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      });

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow(SkribbleAuthError);
    });
  });

  describe('token validation', () => {
    it('should validate token successfully', async () => {
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });

      const accessToken = await skribble.init(mockCredentials.access_token);
      expect(accessToken).toBe(mockCredentials.access_token);
    });

    it('should throw on invalid token', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 401,
          data: { message: 'Invalid token' }
        }
      });

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle server errors during token validation', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      });

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow(SkribbleAuthError);
    });
  });

  describe('makeRequest', () => {
    beforeEach(async () => {
      // Initialize with token
      mockAxiosInstance.request.mockResolvedValueOnce({ data: [] });
      await skribble.init(mockCredentials.access_token);
      mockAxiosInstance.request.mockReset();
    });

    it('should make successful request', async () => {
      const mockResponse = { data: { success: true } };
      mockAxiosInstance.request.mockResolvedValueOnce(mockResponse);

      const client = SkribbleClient.getInstance();
      const result = await client.makeRequest('GET', '/test');
      
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle blob response type', async () => {
      const mockBuffer = Buffer.from('test');
      mockAxiosInstance.request.mockResolvedValueOnce({ data: mockBuffer });

      const client = SkribbleClient.getInstance();
      const result = await client.makeRequest('GET', '/test', null, null, 'blob');
      
      expect(result).toBeInstanceOf(Blob);
    });

    it('should throw if not authenticated', async () => {
      (SkribbleClient as any).instance = null;
      const client = SkribbleClient.getInstance();

      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle non-axios errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new Error('Unknown error'));

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle unknown error types', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce('unexpected error');

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle 401 errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle 403 errors', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        }
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle axios errors without response', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        message: 'Network Error'
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle axios errors without data', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500
        }
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle 202 status code', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 202,
          data: { message: 'Resource not ready' }
        }
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow(SkribbleAPIError);
    });

    it('should handle axios errors with custom message', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { message: 'Custom error message' }
        }
      });

      const client = SkribbleClient.getInstance();
      await expect(client.makeRequest('GET', '/test'))
        .rejects
        .toThrow('Custom error message');
    });
  });

  describe('validateAccessToken', () => {
    it('should handle empty token', async () => {
      await expect(skribble.init(''))
        .rejects
        .toThrow('No authentication credentials provided');
    });

    it('should handle SkribbleAuthError during validation', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new SkribbleAuthError('Invalid token'));

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow('Unable to validate access token. It may be expired or invalid.');
    });

    it('should handle 500 error during validation', async () => {
      mockAxiosInstance.request.mockRejectedValueOnce(new SkribbleAPIError('Server error', 500));

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow('Unable to validate access token. It may be expired or invalid.');
    });

    it('should handle other errors during validation', async () => {
      const error = new Error('Unknown error');
      mockAxiosInstance.request.mockRejectedValueOnce(error);

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow('Unable to validate access token. It may be expired or invalid.');
    });

    it('should handle errors that are neither SkribbleAuthError nor SkribbleAPIError', async () => {
      const error = new TypeError('Type error');
      mockAxiosInstance.request.mockRejectedValueOnce(error);

      await expect(skribble.init(mockCredentials.access_token))
        .rejects
        .toThrow('Unable to validate access token. It may be expired or invalid.');
    });
  });

  describe('authenticateWithCredentials', () => {
    it('should handle axios errors without response', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        message: 'Network Error'
      });

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow(SkribbleAuthError);
    });

    it('should handle non-Error objects', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce('Unexpected error');

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow('An unknown error occurred during authentication');
    });

    it('should handle axios errors with response but no data', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500
        }
      });

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow('An unknown error occurred during authentication');
    });

    it('should handle axios errors with response but no status', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        response: {}
      });

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow('An unknown error occurred during authentication');
    });

    it('should handle axios errors with response but no message', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 500,
          data: {}
        }
      });

      await expect(skribble.init(mockCredentials.username, mockCredentials.api_key))
        .rejects
        .toThrow('An unknown error occurred during authentication');
    });
  });

  describe('SkribbleClient', () => {
    it('should create a new instance with default baseURL', () => {
      const client = SkribbleClient.getInstance();
      expect((client as any).baseURL).toBe('https://api.skribble.com/v2');
      expect((client as any).accessToken).toBeNull();
    });

    it('should reuse the same instance', () => {
      const client1 = SkribbleClient.getInstance();
      const client2 = SkribbleClient.getInstance();
      expect(client1).toBe(client2);
    });
  });
}); 