import { SkribbleError, SkribbleAuthError, SkribbleAPIError, SkribbleValidationError, handleSkribbleError } from '../src/errors';

describe('Skribble Errors', () => {
  describe('SkribbleError', () => {
    it('should create base error with message', () => {
      const error = new SkribbleError('Test error');
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('SkribbleError');
      expect(error instanceof Error).toBe(true);
    });
  });

  describe('SkribbleAuthError', () => {
    it('should create auth error with message', () => {
      const error = new SkribbleAuthError('Auth failed');
      expect(error.message).toBe('Auth failed');
      expect(error.name).toBe('SkribbleAuthError');
      expect(error instanceof SkribbleError).toBe(true);
    });
  });

  describe('SkribbleAPIError', () => {
    it('should create API error with message and status code', () => {
      const error = new SkribbleAPIError('API error', 400);
      expect(error.message).toBe('API error');
      expect(error.statusCode).toBe(400);
      expect(error.name).toBe('SkribbleAPIError');
      expect(error instanceof SkribbleError).toBe(true);
    });

    it('should store response data', () => {
      const responseData = { detail: 'Invalid input' };
      const error = new SkribbleAPIError('API error', 400, responseData);
      expect(error.responseData).toEqual(responseData);
    });
  });

  describe('SkribbleValidationError', () => {
    it('should create validation error with message', () => {
      const error = new SkribbleValidationError('Validation failed');
      expect(error.message).toBe('Validation failed');
      expect(error.name).toBe('SkribbleValidationError');
      expect(error instanceof SkribbleError).toBe(true);
      expect(error.errors).toEqual([]);
    });

    it('should store validation errors', () => {
      const validationErrors = [
        { field: 'email', msg: 'Invalid email' },
        { field: 'name', msg: 'Name is required' }
      ];
      const error = new SkribbleValidationError('Validation failed', validationErrors);
      expect(error.errors).toEqual(validationErrors);
    });
  });

  describe('handleSkribbleError', () => {
    it('should handle SkribbleError instances', () => {
      const originalError = new SkribbleAuthError('Auth failed');
      const handledError = handleSkribbleError(originalError);
      expect(handledError).toBe(originalError);
    });

    it('should wrap Error instances', () => {
      const originalError = new Error('Network error');
      const handledError = handleSkribbleError(originalError);
      expect(handledError).toBeInstanceOf(SkribbleError);
      expect(handledError.message).toBe('Network error');
    });

    it('should handle unknown error types', () => {
      const handledError = handleSkribbleError('unexpected error');
      expect(handledError).toBeInstanceOf(SkribbleError);
      expect(handledError.message).toBe('An unknown error occurred');
    });
  });
}); 