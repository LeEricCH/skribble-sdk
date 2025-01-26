import axios, { AxiosInstance, AxiosError, Method } from 'axios';
import { AuthRequest } from './types';
import { SkribbleAuthError, SkribbleAPIError, handleSkribbleError } from './errors';
import * as document from './document';
import * as seal from './seal';

export class SkribbleClient {
  private static instance: SkribbleClient;
  private baseURL: string = 'https://api.skribble.com/v2';
  private accessToken: string | null = null;
  private axiosInstance: AxiosInstance;

  public document = document;
  public seal = seal;

  private constructor() {
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
    });
  }

  public static getInstance(): SkribbleClient {
    if (!SkribbleClient.instance) {
      SkribbleClient.instance = new SkribbleClient();
    }
    return SkribbleClient.instance;
  }

  /**
   * Initialize the Skribble client with API credentials or an access token.
   * 
   * @param usernameOrToken - The API username or a pre-authenticated access token.
   * @param apiKey - The API key (optional if using an access token).
   * @returns A promise that resolves to the access token.
   * @throws {SkribbleAuthError} If the credentials are invalid or the token is invalid/expired.
   * @throws {SkribbleAPIError} If there's an API error during initialization.
   */
  public async init(usernameOrToken: string, apiKey?: string): Promise<string> {
    if (!usernameOrToken) {
      throw new SkribbleAuthError('No authentication credentials provided');
    }
    if (apiKey) {
      // Initialize with username and API key
      return this.authenticateWithCredentials(usernameOrToken, apiKey);
    } else {
      // Initialize with access token
      return this.validateAccessToken(usernameOrToken);
    }
  }

  private async authenticateWithCredentials(username: string, apiKey: string): Promise<string> {
    const authData: AuthRequest = { username, "api-key": apiKey };
    try {
      const response = await this.axiosInstance.post('/access/login', authData);
      this.accessToken = response.data as string;
      return this.accessToken;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401 || error.response?.status === 403) {
          throw new SkribbleAuthError('Invalid credentials');
        }
        throw new SkribbleAPIError(
          error.response?.data?.message || 'An API error occurred',
          error.response?.status || 500,
          error.response?.data
        );
      }
      if (error instanceof Error) {
        throw new SkribbleAuthError(error.message);
      }
      throw new SkribbleAuthError('An unknown error occurred during authentication');
    }
  }

  private async validateAccessToken(token: string): Promise<string> {
    if (!token) {
      throw new SkribbleAuthError('No authentication credentials provided');
    }
    this.accessToken = token;
    try {
      // Perform a test request to verify the token
      await this.makeRequest('GET', '/signature-requests', undefined, { limit: 1 });
      return this.accessToken;
    } catch (error) {
      if (error instanceof SkribbleAuthError) {
        throw new SkribbleAuthError('Invalid or expired token');
      }
      if (error instanceof SkribbleAPIError && error.statusCode === 500) {
        throw new SkribbleAuthError('Unable to validate access token. It may be expired or invalid.');
      }
      throw error;
    }
  }

  public async makeRequest(method: Method, endpoint: string, data?: any, params?: any, responseType?: 'json' | 'blob'): Promise<any> {
    if (!this.accessToken) {
      throw new SkribbleAuthError('Not authenticated. Call init() first.');
    }

    try {
      const response = await this.axiosInstance.request({
        method,
        url: endpoint,
        data,
        params,
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
        responseType: responseType === 'blob' ? 'arraybuffer' : 'json',
      });

      if (responseType === 'blob') {
        return new Blob([response.data]);
      }

      return response.data;
    } catch (error) {
      // Check if error is an Axios error by checking both isAxiosError and response property
      if (error && typeof error === 'object' && 'isAxiosError' in error && 'response' in error) {
        const axiosError = error as AxiosError<{ message?: string }>;
        if (axiosError.response?.status === 401 || axiosError.response?.status === 403) {
          throw new SkribbleAuthError('Invalid or expired token');
        }
        // Pass through 202 status with the status code
        if (axiosError.response?.status === 202) {
          throw new SkribbleAPIError(
            axiosError.response.data?.message || 'Resource not ready',
            202,
            axiosError.response.data
          );
        }
        throw new SkribbleAPIError(
          axiosError.response?.data?.message || 'An API error occurred',
          axiosError.response?.status || 500,
          axiosError.response?.data
        );
      }
      if (error instanceof Error) {
        throw new SkribbleAPIError(error.message, 500);
      }
      throw new SkribbleAPIError('An unknown error occurred', 500);
    }
  }
}