# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class UtmStage(models.Model):
    """Stage for utm campaigns."""

    _name = 'utm.stage'
    _description = 'Campaign Stage'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=1)
