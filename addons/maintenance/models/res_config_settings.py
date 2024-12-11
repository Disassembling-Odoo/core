# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_maintenance_worksheet = fields.Boolean(string="Custom Maintenance Worksheets")
