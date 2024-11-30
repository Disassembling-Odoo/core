# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.ormapping import fields


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    sms_template_id = fields.Many2one('sms.template', string="SMS Template",
        domain=[('model', '=', 'project.project')],
        help="If set, an SMS Text Message will be automatically sent to the customer when the project reaches this stage.")
