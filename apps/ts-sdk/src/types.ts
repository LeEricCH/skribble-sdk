export interface AuthRequest {
  username: string;
  "api-key": string;
}

export interface SignerIdentityData {
  email_address: string;
  mobile_number?: string;
  first_name?: string;
  last_name?: string;
  language?: string;
}

export interface Image {
  content_type: string;
  content: string;
}

export interface Position {
  x: number;
  y: number;
  width: number;
  height: number;
  page: string;
  rotation?: number;
}

export interface VisualSignature {
  position: Position;
  image: Image;
}

export interface Signature {
  account_email?: string;
  signer_identity_data?: SignerIdentityData;
  visual_signature?: VisualSignature;
  sequence?: number;
  notify?: boolean;
  language?: string;
}

export interface SignatureRequest {
  title: string;
  message?: string;
  content?: string;
  content_type?: string;
  file_url?: string;
  document_id?: string;
  legislation?: string;
  quality?: string;
  cc_email_addresses?: string[];
  callback_success_url?: string;
  callback_error_url?: string;
  callback_update_url?: string;
  custom?: string;
  write_access?: string[];
  signatures?: Signature[];
}

export interface Document {
  id: string;
  parent_id?: string;
  title: string;
  content_type: string;
  size: number;
  page_count?: number;
  page_width?: number;
  page_height?: number;
  owner: string;
}

export interface Seal {
  title?: string;
  content: string;
  account_name?: string;
  visual_signature?: VisualSignature;
}

export interface DocumentRequest {
  title: string;
  content_type?: string;
  content?: string;
  file_url?: string;
  write_access?: string[];
}

export interface Attachment {
  filename: string;
  content: string;
  content_type: string;
}