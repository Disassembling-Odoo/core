from odoo.microkernel.ormapping import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_scope = fields.Selection(
        selection_add=[('merch', 'Merchandise'), ('invest', 'Investment')],
    )
