# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.ormapping import fields


class AccountTax(models.Model):

    _inherit = "account.tax"

    l10n_uy_tax_category = fields.Selection([
        ('vat', 'VAT'),
    ], string="Tax Category", help="UY: Use to group the transactions in the Financial Reports required by DGI")
