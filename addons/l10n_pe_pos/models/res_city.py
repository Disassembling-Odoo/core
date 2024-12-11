# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api


class ResCity(models.Model):
    _name = "res.city"
    _inherit = ["res.city", "pos.load.mixin"]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ["name", "country_id", "state_id"]
