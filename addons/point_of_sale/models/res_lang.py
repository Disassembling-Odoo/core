from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api


class ResLang(models.Model):
    _name = 'res.lang'
    _inherit = ['res.lang', 'pos.load.mixin']

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'code', 'flag_image_url', 'display_name']
