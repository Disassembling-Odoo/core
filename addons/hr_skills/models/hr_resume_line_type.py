# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResumeLineType(models.Model):
    _name = 'hr.resume.line.type'
    _description = "Type of a resume line"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
