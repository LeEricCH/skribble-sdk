from .operations import (
    create,
    get,
    delete,
    list,
    update,
    withdraw,
    remind
)

# Create submodules for attachment and signer operations
class AttachmentOperations:
    from .operations import (
        add_attachment as add,
        download_attachment as download,
        delete_attachment as delete,
        list_attachments as list
    )
    add = staticmethod(add)
    download = staticmethod(download)
    delete = staticmethod(delete)
    list = staticmethod(list)

class SignerOperations:
    from .operations import (
        add_signer as add,
        remove_signer as remove,
        replace_signers as replace
    )
    add = staticmethod(add)
    remove = staticmethod(remove)
    replace = staticmethod(replace)

# Initialize submodules
attachment = AttachmentOperations()
signer = SignerOperations()

__all__ = [
    'create',
    'get',
    'delete',
    'list',
    'update',
    'withdraw',
    'remind',
    'attachment',
    'signer'
]