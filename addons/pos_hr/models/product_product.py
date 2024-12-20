from odoo.microkernel.ormapping import models
from odoo.microkernel import api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result.append('all_product_tag_ids')
        return result
