# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    events_app_name = fields.Char('Events App Name', related='website_id.events_app_name', readonly=False)
