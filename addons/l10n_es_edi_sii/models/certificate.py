from odoo.microkernel.ormapping import models, fields


class Certificate(models.Model):
    _inherit = 'certificate.certificate'

    scope = fields.Selection(
        selection_add=[
            ('sii', 'SII')
        ],
    )
