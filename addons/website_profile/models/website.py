# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class Website(models.Model):
    _inherit = 'website'

    karma_profile_min = fields.Integer(string="Minimal karma to see other user's profile", default=150)
