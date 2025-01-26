export class SkribbleError extends Error {
  public statusCode?: number;
  public responseData?: any;

  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class SkribbleAuthError extends SkribbleError {}

export class SkribbleAPIError extends SkribbleError {
  public statusCode: number;
  public responseData: any;

  constructor(message: string, statusCode: number, responseData?: any) {
    super(message);
    this.statusCode = statusCode;
    this.responseData = responseData;
  }
}

export class SkribbleValidationError extends SkribbleError {
  public errors: any[];

  constructor(message: string, errors: any[] = []) {
    super(message);
    this.errors = errors;
  }
}

export function handleSkribbleError(error: unknown): SkribbleError {
  if (error instanceof SkribbleError) {
    return error;
  } else if (error instanceof Error) {
    return new SkribbleError(error.message);
  } else {
    return new SkribbleError('An unknown error occurred');
  }
}