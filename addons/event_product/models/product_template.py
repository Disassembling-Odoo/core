from odoo.microkernel.ormapping import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_tracking = fields.Selection(selection_add=[
        ('event', 'Event Registration'),
    ], ondelete={'event': 'set default'})

    def _service_tracking_blacklist(self):
        return super()._service_tracking_blacklist() + ['event']
