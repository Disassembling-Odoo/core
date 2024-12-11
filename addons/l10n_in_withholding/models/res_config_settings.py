from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_in_withholding_account_id = fields.Many2one(
        related='company_id.l10n_in_withholding_account_id',
        readonly=False,
    )
    l10n_in_withholding_journal_id = fields.Many2one(
        related='company_id.l10n_in_withholding_journal_id',
        readonly=False,
    )
