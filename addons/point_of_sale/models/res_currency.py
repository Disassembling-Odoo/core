from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api

class ResCurrency(models.Model):
    _name = 'res.currency'
    _inherit = ['res.currency', 'pos.load.mixin']

    @api.model
    def _load_pos_data_domain(self, data):
        return [('id', '=', data['pos.config']['data'][0]['currency_id'])]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'symbol', 'position', 'rounding', 'rate', 'decimal_places', 'iso_numeric']
