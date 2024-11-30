from odoo import models
from odoo.ormapping import fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_ca_pst = fields.Char(string='PST number', help='Canadian Provincial Tax Identification Number')
