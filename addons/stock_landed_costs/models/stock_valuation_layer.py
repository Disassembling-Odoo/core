# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    stock_landed_cost_id = fields.Many2one('stock.landed.cost', 'Landed Cost')
