from odoo import models
from odoo.ormapping import fields


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    l10n_din5008_printing_date = fields.Date(default=fields.Date.today, store=False)
