from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['l10n_in_tax_type']
        return fields
