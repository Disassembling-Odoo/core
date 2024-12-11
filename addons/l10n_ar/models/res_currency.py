# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models, fields


class ResCurrency(models.Model):

    _inherit = "res.currency"

    l10n_ar_afip_code = fields.Char('AFIP Code', size=4, help='This code will be used on electronic invoice')
