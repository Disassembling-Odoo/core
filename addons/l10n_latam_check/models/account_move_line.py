# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models, fields


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    l10n_latam_check_ids = fields.One2many('l10n_latam.check', 'outstanding_line_id', string='Checks')
