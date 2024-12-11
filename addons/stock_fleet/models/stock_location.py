from odoo.microkernel.ormapping import models, fields


class StockPickingBatch(models.Model):
    _inherit = 'stock.location'

    is_a_dock = fields.Boolean("Is a Dock Location")
