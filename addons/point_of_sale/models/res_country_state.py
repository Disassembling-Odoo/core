from odoo import models
from odoo.microkernel.api import api


class ResCountryState(models.Model):
    _name = 'res.country.state'
    _inherit = ['res.country.state', 'pos.load.mixin']

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'code', 'country_id']
