from odoo import models
from odoo.ormapping import fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    l10n_pt_taxonomy_code = fields.Integer(string="Taxonomy code")
