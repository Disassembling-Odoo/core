from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api


class Product(models.Model):
    _inherit = 'product.product'

    @api.onchange('service_tracking')
    def _onchange_type_event_booth(self):
        if self.service_tracking == 'event_booth':
            self.invoice_policy = 'order'
