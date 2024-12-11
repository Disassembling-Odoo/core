# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_analytic_accounting = fields.Boolean(string='Analytic Accounting', implied_group='analytic.group_analytic_accounting')
