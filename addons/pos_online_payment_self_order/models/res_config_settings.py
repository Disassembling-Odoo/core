# -*- coding: utf-8 -*-
from odoo.microkernel.ormapping import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_self_order_online_payment_method_id = fields.Many2one(related='pos_config_id.self_order_online_payment_method_id', readonly=False)
