from odoo import models
from odoo.microkernel.api import api


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _load_pos_data_fields(self):
        return ['id', 'name', 'state']

    @api.model
    def _load_pos_data_domain(self):
        return [('name', '=', 'pos_settle_due')]

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain()
        fields = self._load_pos_data_fields()
        return {
            'data': self.search_read(domain, fields, load=False),
            'fields': self._load_pos_data_fields(),
        }
