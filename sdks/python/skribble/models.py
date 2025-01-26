# ----------------------------------------
# THIS FILE IS GENERATED - DO NOT EDIT
# Run generator via: pnpm generate-models
# Source: schemas/models.yaml
# ----------------------------------------

from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from difflib import get_close_matches
from .exceptions import SkribbleValidationError

# Type aliases
Blob = bytes

class DocumentContent(BaseModel):
    """Document content type that can be either a Blob or string"""
    content: Union[bytes, str]
    def __init__(self, content: Union[bytes, str]):
        super().__init__(content=content)

    @property
    def raw_bytes(self) -> bytes:
        """Get content as raw bytes."""
        if isinstance(self.content, bytes):
            return self.content
        import base64
        return base64.b64decode(self.content)

    @property
    def base64(self) -> str:
        """Get content as base64 string."""
        if isinstance(self.content, str):
            return self.content
        import base64
        return base64.b64encode(self.content).decode()


class Image(BaseModel):
    """Image data with content type and content"""
    content_type: str
    content: str

class Position(BaseModel):
    """Position details for visual elements"""
    x: float
    y: float
    width: float
    height: float
    page: str
    rotation: Optional[float] = Field(default=0)

class SignerIdentityData(BaseModel):
    """Identity data for no-account signers"""
    email_address: str = Field(description='Email address of no-account-signer')
    mobile_number: Optional[str] = Field(default=None, description='Mobile number of no-account-signer')
    first_name: Optional[str] = Field(default=None, description='First name of no-account-signer')
    last_name: Optional[str] = Field(default=None, description='Last name of no-account-signer')
    language: Optional[str] = Field(default=None, description='Language for communication with the signer')

class Document(BaseModel):
    """Represents a document"""
    id: str = Field(description='ID of the Document object')
    parent_id: Optional[str] = Field(default=None, description='ID of the previous version of the Document object')
    title: str = Field(description='Given title of the document')
    content_type: str = Field(description='Content type of the document')
    size: int = Field(description='Size in bytes of the document')
    page_count: Optional[int] = Field(default=None, description='Number of pages in the document')
    page_width: Optional[int] = Field(default=None, description='Width of the document pages')
    page_height: Optional[int] = Field(default=None, description='Height of the document pages')
    owner: str = Field(description='Owner of the document')

class VisualSignature(BaseModel):
    """Visual signature with position and optional image"""
    form_field: Optional[str] = Field(default=None, description="Name of the document's form field in which the signature is placed. Takes precedence before positions")
    position: "Position"
    image: Optional["Image"] = Field(default=None)

class Signature(BaseModel):
    """Represents a signature in a signature request"""
    account_email: Optional[str] = Field(default=None, description="Signer's e-mail address")
    signer_identity_data: Optional["SignerIdentityData"] = Field(default=None)
    visual_signature: Optional["VisualSignature"] = Field(default=None)
    sequence: Optional[int] = Field(default=None, description='Define a signing sequence for signers')
    notify: Optional[bool] = Field(default=True, description='Send e-mails to notify the signer')
    language: Optional[str] = Field(default=None, description='Language for communication')

class SignerRequest(BaseModel):
    """Request to add a signer"""
    account_email: Optional[str] = Field(default=None, description="Signer's e-mail address")
    signer_identity_data: Optional["SignerIdentityData"] = Field(default=None)
    visual_signature: Optional["VisualSignature"] = Field(default=None)
    sequence: Optional[int] = Field(default=None)
    notify: Optional[bool] = Field(default=True)
    language: Optional[str] = Field(default=None)

class DocumentResponse(BaseModel):
    """Response object for a document"""
    id: str = Field(description='ID of the Document object')
    parent_id: Optional[str] = Field(default=None, description='ID of the previous version of the Document object')
    title: str = Field(description='Given title of the document')
    content_type: str = Field(description='Content type of the document (always application/pdf)')
    size: int = Field(description='Size in bytes of the document')
    page_count: Optional[int] = Field(default=None, description='Number of pages of the document')
    page_width: Optional[int] = Field(default=None, description='Width of the document in pixel')
    page_height: Optional[int] = Field(default=None, description='Height of the document in pixel')
    signature_fields: Optional[List[object]] = Field(default=None, description='PDF AcroForm signature fields found in the document')
    read_access: List[str] = Field(description='Array of users with read access')
    write_access: List[str] = Field(description='Array of users with write access')
    created_at: str = Field(description='Timestamp at which the document was created')
    updated_at: Optional[str] = Field(default=None, description='Timestamp at which the document was last updated')

class AuthRequest(BaseModel):
    """Authentication request for the API"""
    username: str = Field(description='API username')
    api_key: str = Field(description='API key')

class SignatureRequest(BaseModel):
    """Represents a signature request"""
    title: str = Field(description='Title of the signature request')
    message: Optional[str] = Field(default=None, description='Message sent to the participants')
    content: Optional[str] = Field(default=None, description='Base64 encoded bytes of document')
    content_type: Optional[str] = Field(default=None, description='Content type of bytes sent in content')
    file_url: Optional[str] = Field(default=None, description='Publicly accessible URL for document download')
    document_id: Optional[str] = Field(default=None, description='Document ID of an existing document on Skribble')
    legislation: Optional[str] = Field(default=None, description='Legislation of the signatures (ZERTES or EIDAS). Only important for QES signatures')
    quality: Optional[str] = Field(default=None, description='Minimal quality of the signatures (AES, AES_MINIMAL, SES or QES)')
    cc_email_addresses: Optional[List[str]] = Field(default=None, description='CC email addresses')
    callback_success_url: Optional[str] = Field(default=None, description='Callback-URL for success')
    callback_error_url: Optional[str] = Field(default=None, description='Callback-URL for errors')
    callback_update_url: Optional[str] = Field(default=None, description='Callback-URL for updates')
    custom: Optional[str] = Field(default=None, description='Custom field for own/customer settings')
    write_access: Optional[List[str]] = Field(default=None, description='Users with full write access')
    signatures: Optional[List["Signature"]] = Field(default=None)

class AttachmentResponse(BaseModel):
    """Response object for an attachment"""
    attachment_id: str = Field(description='ID of the attachment')
    filename: str = Field(description='Name of the attachment file')

class SignatureResponse(BaseModel):
    """Response object for a signature"""
    sid: str = Field(description='ID of the SignatureRequest object')
    account_email: Optional[str] = Field(default=None, description='Email address of the signer')
    signer_identity_data: Optional["SignerIdentityData"] = Field(default=None, description='Contains the given first_name and last_name of the signer')
    sequence: Optional[int] = Field(default=None, description='Signing sequence for the signer')
    status_code: str = Field(description='Status of the signature')
    notify: Optional[bool] = Field(default=None, description='Given identifier, if the signer will be notified about changes on this signature request')
    signed_at: Optional[str] = Field(default=None, description='Visible only after the signature. Timestamp UTC at which the signature was executed')
    signed_quality: Optional[str] = Field(default=None, description='Visible only after the signature. Quality level with which the signature was executed')
    signed_legislation: Optional[str] = Field(default=None, description='Visible only after the signature. Legislation with which the signature was executed')
    last_viewed_at: Optional[str] = Field(default=None, description='Timestamp UTC at which the signer opened/viewed the document the last time')

class SignatureRequestResponse(BaseModel):
    """Response object for a signature request"""
    id: str = Field(description='ID of the SignatureRequest object')
    title: str = Field(description='Given title for the signature request')
    message: Optional[str] = Field(default=None, description='Given message that is shown to the participants')
    document_id: str = Field(description='ID of the Document object')
    legislation: Optional[str] = Field(default=None, description='Given legislation of the signatures for this signature request')
    quality: Optional[str] = Field(default=None, description='Given quality of the signatures for this signature request')
    signing_url: Optional[str] = Field(default=None, description="Deprecated. Please use the signing_url inside the user's Signature entry")
    status_overall: str = Field(description='Status of the signature request')
    signatures: List["SignatureResponse"] = Field(description='Array of signatures within this signature request')
    cc_email_addresses: Optional[List[str]] = Field(default=None, description='Given array of email-addresses that will be additionally notified upon completed signature request')
    owner: str = Field(description='Creator of the SignatureRequest object')
    read_access: Optional[List[str]] = Field(default=None, description='Array of users with read access on the signature request')
    write_access: Optional[List[str]] = Field(default=None, description='Array of users with write access on the signature request')
    created_at: Optional[str] = Field(default=None, description='Timestamp at which the signature request was created')
    updated_at: Optional[str] = Field(default=None, description='Timestamp at which the signature request was last updated')
    attachments: Optional[List["AttachmentResponse"]] = Field(default=None, description='Array of attachments associated with this signature request')

class DocumentRequest(BaseModel):
    """Request to create a new document"""
    title: str = Field(description='Title of the document')
    content_type: Optional[str] = Field(default=None, description='Content type of bytes sent in content')
    content: Optional[str] = Field(default=None, description='Base64 encoded bytes of document')
    file_url: Optional[str] = Field(default=None, description='Publicly accessible URL for document download')
    write_access: Optional[List[str]] = Field(default=None, description='E-mail addresses with write access to the object')

class UpdateSignatureRequest(BaseModel):
    """Request to update a signature request"""
    id: str = Field(description='ID of the signature request to update')
    title: Optional[str] = Field(default=None, description='New title of the signature request')
    message: Optional[str] = Field(default=None, description='New message sent to the participants')
    legislation: Optional[str] = Field(default=None, description='New legislation of the signatures')
    quality: Optional[str] = Field(default=None, description='New minimal quality of the signatures')
    cc_email_addresses: Optional[List[str]] = Field(default=None, description='New CC email addresses')
    callback_success_url: Optional[str] = Field(default=None, description='New callback-URL for success')
    callback_error_url: Optional[str] = Field(default=None, description='New callback-URL for errors')
    callback_update_url: Optional[str] = Field(default=None, description='New callback-URL for updates')
    custom: Optional[str] = Field(default=None, description='New custom field for own/customer settings')
    write_access: Optional[List[str]] = Field(default=None, description='New users with full write access')

class Attachment(BaseModel):
    """Attachment for a document"""
    title: str = Field(description='Title of the attachment')
    content: str = Field(description='Base64 encoded bytes of the attachment')
    content_type: str = Field(description='Content type of the attachment')

class AttachmentRequest(BaseModel):
    """Request to add an attachment to a signature request"""
    filename: str = Field(description='Name of the attachment file')
    content_type: str = Field(description='Content type of the attachment')
    content: str = Field(description='Base64 encoded content of the attachment')

class SealRequest(BaseModel):
    """Request to seal a document"""
    title: str = Field(description='Title of the seal document')
    content: str = Field(description='Base64 encoded bytes of document')
    account_name: Optional[str] = Field(default=None, description='Specifies the seal to use for sealing')
    visual_signature: Optional["VisualSignature"] = Field(default=None)

class Seal(BaseModel):
    """Seal for a document"""
    title: Optional[str] = Field(default=None, description='Title of the seal document')
    content: str = Field(description='Base64 encoded bytes of document')
    account_name: Optional[str] = Field(default=None, description='Specifies the seal to use for sealing')
    visual_signature: Optional["VisualSignature"] = Field(default=None)

class SealResponse(BaseModel):
    """Response from seal operations"""
    document_id: str = Field(description='The document ID')
