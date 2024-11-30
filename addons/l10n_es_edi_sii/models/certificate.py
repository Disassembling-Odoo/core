from odoo import models
from odoo.ormapping import fields


class Certificate(models.Model):
    _inherit = 'certificate.certificate'

    scope = fields.Selection(
        selection_add=[
            ('sii', 'SII')
        ],
    )
