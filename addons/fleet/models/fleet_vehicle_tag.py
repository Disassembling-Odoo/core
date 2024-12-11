# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class FleetVehicleTag(models.Model):
    _name = 'fleet.vehicle.tag'
    _description = 'Vehicle Tag'

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color')

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists!")]
