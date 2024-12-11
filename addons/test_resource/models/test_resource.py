# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResourceTest(models.Model):
    _description = 'Test Resource Model'
    _name = 'resource.test'
    _inherit = ['resource.mixin']

    name = fields.Char()
