from odoo import models
from odoo.ormapping import fields


class Event(models.Model):
    _inherit = 'event.event'

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)
