# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.technology.utils import first as fields_first
from odoo.microkernel.api import api
from odoo.microkernel.ormapping import models, fields

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_calendar_event_id = fields.Many2one(
        'calendar.event', string="Next Activity Calendar Event",
        compute='_compute_activity_calendar_event_id', groups="base.group_user")

    @api.depends('activity_ids.calendar_event_id')
    def _compute_activity_calendar_event_id(self):
        """This computes the calendar event of the next activity.
        It evaluates to false if there is no such event."""
        for record in self:
            record.activity_calendar_event_id = fields_first(record.activity_ids).calendar_event_id
