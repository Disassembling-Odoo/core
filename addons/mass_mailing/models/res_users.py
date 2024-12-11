# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _
from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api

class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    @api.model
    def _get_activity_groups(self):
        """ Update systray name of mailing.mailing from "Mass Mailing"
            to "Email Marketing".
        """
        activities = super()._get_activity_groups()
        for activity in activities:
            if activity.get('model') == 'mailing.mailing':
                activity['name'] = _('Email Marketing')
                break
        return activities
