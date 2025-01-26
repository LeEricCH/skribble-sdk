import { SkribbleClient } from './client';
import * as signatureRequest from './signature_request';
import * as document from './document';
import * as seal from './seal';
import { SkribbleAuthError, SkribbleAPIError, SkribbleValidationError, handleSkribbleError } from './errors';
import * as Types from './types';

export { SkribbleAuthError, SkribbleAPIError, SkribbleValidationError, handleSkribbleError };
export { Types };

/**
 * The main Skribble SDK object.
 */
const skribble = {
  init: async (usernameOrToken: string, apiKey?: string): Promise<string> => {
    const client = SkribbleClient.getInstance();
    return client.init(usernameOrToken, apiKey);
  },
  signature_request: signatureRequest,
  document,
  seal,
  SkribbleAuthError,
  SkribbleAPIError,
  SkribbleValidationError,
  handleSkribbleError
};

export default skribble;