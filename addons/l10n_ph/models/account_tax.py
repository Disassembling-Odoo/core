# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_ph_atc = fields.Char("Philippines ATC")
