from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator, model_validator
from difflib import get_close_matches

class AuthRequest(BaseModel):
    username: str = Field(..., description="API username")
    api_key: str = Field(..., alias="api-key", description="API key")

class SignerIdentityData(BaseModel):
    email_address: EmailStr = Field(..., description="Email address of no-account-signer")
    mobile_number: Optional[str] = Field(None, max_length=100, description="Mobile number of no-account-signer")
    first_name: Optional[str] = Field(None, max_length=1024, description="First name of no-account-signer")
    last_name: Optional[str] = Field(None, max_length=1024, description="Last name of no-account-signer")
    language: Optional[str] = Field(None, description="Language for communication with the signer")

    @model_validator(mode='before')
    def check_fields(cls, values):
        valid_fields = cls.model_fields.keys()
        for field in values:
            if field not in valid_fields:
                close_matches = get_close_matches(field, valid_fields, n=1, cutoff=0.6)
                if close_matches:
                    raise ValueError(f"Invalid field '{field}'. Did you mean '{close_matches[0]}'?")
                else:
                    raise ValueError(f"Invalid field '{field}'. Valid fields are: {', '.join(valid_fields)}")
        return values

class Image(BaseModel):
    content_type: str
    content: str

class Position(BaseModel):
    x: float
    y: float
    width: float
    height: float
    page: str
    rotation: float = 0

class VisualSignature(BaseModel):
    position: Position
    image: Image

class Seal(BaseModel):
    title: Optional[str] = Field(None, max_length=1024, description="Title of the seal document")
    content: str = Field(..., description="Base64 encoded bytes of document")
    account_name: Optional[str] = Field(None, max_length=256, description="Specifies the seal to use for sealing")
    visual_signature: Optional[VisualSignature] = None

class Signature(BaseModel):
    """
    Represents a signature in a signature request.

    Attributes:
        account_email (Optional[EmailStr]): Signer's e-mail address.
        signer_identity_data (Optional[SignerIdentityData]): Identity data for no-account signers.
        visual_signature (Optional[VisualSignature]): Visual signature details.
        sequence (Optional[int]): Define a signing sequence for signers (1-999).
        notify (Optional[bool]): Send e-mails to notify the signer.
        language (Optional[str]): Language for communication.
    """
    account_email: Optional[EmailStr] = Field(None, description="Signer's e-mail address")
    signer_identity_data: Optional[SignerIdentityData] = None
    visual_signature: Optional[Dict] = None
    sequence: Optional[int] = Field(None, ge=1, le=999, description="Define a signing sequence for signers")
    notify: Optional[bool] = Field(True, description="Send e-mails to notify the signer")
    language: Optional[str] = Field(None, description="Language for communication")

    @model_validator(mode='after')
    def check_email_or_identity(cls, values):
        if not values.account_email and not values.signer_identity_data:
            raise ValueError("Either 'account_email' or 'signer_identity_data' must be provided")
        return values

    @validator('sequence')
    def check_sequence(cls, v):
        if v is not None and (v < 1 or v > 999):
            raise ValueError("Sequence must be between 1 and 999")
        return v

class SignatureRequest(BaseModel):
    """
    Represents a signature request.

    Attributes:
        title (str): Title of the signature request.
        message (Optional[str]): Message sent to the participants.
        content (Optional[str]): Base64 encoded bytes of document.
        content_type (Optional[str]): Content type of bytes sent in content.
        file_url (Optional[str]): Publicly accessible URL for document download.
        document_id (Optional[str]): Document ID of an existing document on Skribble.
        legislation (Optional[str]): Legislation of the signatures.
        quality (Optional[str]): Minimal quality of the signatures.
        cc_email_addresses (Optional[List[EmailStr]]): CC email addresses.
        callback_success_url (Optional[str]): Callback-URL for success.
        callback_error_url (Optional[str]): Callback-URL for errors.
        callback_update_url (Optional[str]): Callback-URL for updates.
        custom (Optional[str]): Custom field for own/customer settings.
        write_access (Optional[List[EmailStr]]): Users with full write access.
        signatures (Optional[List[Signature]]): List of signatures for this request.
    """
    title: str = Field(..., max_length=1024, description="Title of the signature request")
    message: Optional[str] = Field(None, max_length=1024, description="Message sent to the participants")
    content: Optional[str] = Field(None, description="Base64 encoded bytes of document")
    content_type: Optional[str] = Field(None, max_length=1024, description="Content type of bytes sent in content")
    file_url: Optional[str] = Field(None, max_length=2048, description="Publicly accessible URL for document download")
    document_id: Optional[str] = Field(None, max_length=100, description="Document ID of an existing document on Skribble")
    legislation: Optional[str] = Field(None, max_length=100, description="Legislation of the signatures")
    quality: Optional[str] = Field(None, max_length=100, description="Minimal quality of the signatures")
    cc_email_addresses: Optional[List[EmailStr]] = Field(None, description="CC email addresses")
    callback_success_url: Optional[str] = Field(None, max_length=2048, description="Callback-URL for success")
    callback_error_url: Optional[str] = Field(None, max_length=2048, description="Callback-URL for errors")
    callback_update_url: Optional[str] = Field(None, max_length=2048, description="Callback-URL for updates")
    custom: Optional[str] = Field(None, max_length=10000, description="Custom field for own/customer settings")
    write_access: Optional[List[EmailStr]] = Field(None, description="Users with full write access")
    signatures: Optional[List[Signature]] = None

    @model_validator(mode='after')
    def check_document_source(self):
        content = self.content
        file_url = self.file_url
        document_id = self.document_id
        if not any([content, file_url, document_id]):
            raise ValueError("At least one of 'content', 'file_url', or 'document_id' must be provided")
        return self

    class Config:
        json_encoders = {
            HttpUrl: str
        }

class Document(BaseModel):
    id: str = Field(..., description="ID of the Document object")
    parent_id: Optional[str] = Field(None, description="ID of the previous version of the Document object")
    title: str = Field(..., max_length=1024, description="Given title of the document")
    content_type: str = Field(..., description="Content type of the document")
    size: int = Field(..., description="Size in bytes of the document")
    page_count: Optional[int] = Field(None, description="Number of pages in the document")
    page_width: Optional[int] = Field(None, description="Width of the document pages")
    page_height: Optional[int] = Field(None, description="Height of the document pages")
    owner: str = Field(..., description="Owner of the document")

class DocumentRequest(BaseModel):
    title: str = Field(..., max_length=1024, description="Title of the document")
    content_type: Optional[str] = Field(None, max_length=100, description="Content type of bytes sent in content")
    content: Optional[str] = Field(None, description="Base64 encoded bytes of document")
    file_url: Optional[str] = Field(None, max_length=2048, description="Publicly accessible URL for document download")
    write_access: Optional[List[EmailStr]] = Field(None, description="E-mail addresses with write access to the object")

    @model_validator(mode='after')
    def check_content_or_file_url(cls, values):
        if bool(values.content) == bool(values.file_url):
            raise ValueError("Either 'content' or 'file_url' must be provided, but not both")
        if values.content and not values.content_type:
            raise ValueError("'content_type' must be provided when 'content' is used")
        return values
