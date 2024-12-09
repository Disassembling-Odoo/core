# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.microkernel.api import api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_product_types_allow_zero_price(self):
        return super()._get_product_types_allow_zero_price() + ["event_booth"]
