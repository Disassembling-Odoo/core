# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel import api
from odoo.microkernel.ormapping import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    event_ticket_id = fields.Many2one('event.event.ticket', string='Event Ticket')
    event_registration_ids = fields.One2many('event.registration', 'pos_order_line_id', string='Event Registrations')

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['event_ticket_id', 'event_registration_ids']
        return fields
