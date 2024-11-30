from odoo import models
from odoo.ormapping import fields


class StockPickingBatch(models.Model):
    _inherit = 'stock.location'

    is_a_dock = fields.Boolean("Is a Dock Location")
