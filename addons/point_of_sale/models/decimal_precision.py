from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api


class DecimalPrecision(models.Model):
    _name = 'decimal.precision'
    _inherit = ['decimal.precision', 'pos.load.mixin']

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'digits']
