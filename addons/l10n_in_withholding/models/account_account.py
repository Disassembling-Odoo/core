from odoo.microkernel.ormapping import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    l10n_in_tds_tcs_section_id = fields.Many2one('l10n_in.section.alert', string="TCS/TDS Section")
