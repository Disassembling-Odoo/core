# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.ormapping import fields


class Uom(models.Model):

    _inherit = 'uom.uom'

    l10n_ar_afip_code = fields.Char('Code', help='Argentina: This code will be used on electronic invoice.')
