export type DocumentContent = Blob | string

export type Image = {
  content_type: string;
  content: string;
}

export type Position = {
  x: number;
  y: number;
  width: number;
  height: number;
  page: string;
  rotation?: number;
}

export type SignerIdentityData = {
  email_address: string;
  mobile_number?: string;
  first_name?: string;
  last_name?: string;
  language?: string;
}

export type Document = {
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

export type VisualSignature = {
  form_field?: string;
  position: Position;
  image?: Image;
}

export type Signature = {
  account_email?: string;
  signer_identity_data?: SignerIdentityData;
  visual_signature?: VisualSignature;
  sequence?: number;
  notify?: boolean;
  language?: string;
}

export type SignerRequest = {
  account_email?: string;
  signer_identity_data?: SignerIdentityData;
  visual_signature?: VisualSignature;
  sequence?: number;
  notify?: boolean;
  language?: string;
}

export type DocumentResponse = {
  id: string;
  parent_id?: string;
  title: string;
  content_type: string;
  size: number;
  page_count?: number;
  page_width?: number;
  page_height?: number;
  signature_fields?: { name?: string; status?: string; position?: Position }[];
  read_access: string[];
  write_access: string[];
  created_at: string;
  updated_at?: string;
}

export type AuthRequest = {
  username: string;
  "api-key": string;
}

export type SignatureRequest = {
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

export type AttachmentResponse = {
  attachment_id: string;
  filename: string;
}

export type SignatureResponse = {
  sid?: string;
  account_email?: string;
  signer_identity_data?: any;
  sequence?: number;
  status_code?: string;
  notify?: boolean;
  signed_at?: string;
  signed_quality?: string;
  signed_legislation?: string;
  last_viewed_at?: string;
}

export type SignatureRequestResponse = {
  id: string;
  title: string;
  message?: string;
  document_id: string;
  legislation?: string;
  quality?: string;
  signing_url?: string;
  status_overall: string;
  signatures: SignatureResponse[];
  cc_email_addresses?: string[];
  owner: string;
  read_access?: string[];
  write_access?: string[];
  created_at?: string;
  updated_at?: string;
  attachments?: AttachmentResponse[];
}

export type DocumentRequest = {
  title: string;
  content_type?: string;
  content?: string;
  file_url?: string;
  write_access?: string[];
}

export type UpdateSignatureRequest = {
  id: string;
  title?: string;
  message?: string;
  legislation?: string;
  quality?: string;
  cc_email_addresses?: string[];
  callback_success_url?: string;
  callback_error_url?: string;
  callback_update_url?: string;
  custom?: string;
  write_access?: string[];
}

export type Attachment = {
  title: string;
  content: string;
  content_type: string;
}

export type AttachmentRequest = {
  filename: string;
  content_type: string;
  content: string;
}

export type SealRequest = {
  title: string;
  content: string;
  account_name?: string;
  visual_signature?: VisualSignature;
}

export type Seal = {
  title?: string;
  content: string;
  account_name?: string;
  visual_signature?: VisualSignature;
}

export type SealResponse = {
  document_id: string;
}
