from cryptography.fernet import Fernet

from odoo import models
from odoo.microkernel.api import api


class Key(models.Model):
    _inherit = 'certificate.key'

    @api.model
    def _account_edi_fernet_decrypt(self, key, message):
        key = Fernet(key)
        return key.decrypt(message)
