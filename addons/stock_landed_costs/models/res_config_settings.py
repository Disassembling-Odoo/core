# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.microkernel.ormapping import fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lc_journal_id = fields.Many2one('account.journal', string='Default Journal', related='company_id.lc_journal_id', readonly=False)
