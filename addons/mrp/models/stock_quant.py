from odoo import _
from odoo.microkernel.ormapping import models
from odoo.exceptions import UserError
from odoo.microkernel.api import api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('product_id')
    def _check_kits(self):
        if self.sudo().product_id.filtered("is_kits"):
            raise UserError(_('You should update the components quantity instead of directly updating the quantity of the kit product.'))
