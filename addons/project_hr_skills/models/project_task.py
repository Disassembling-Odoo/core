# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields

class ProjectTask(models.Model):
    _inherit = "project.task"

    user_skill_ids = fields.One2many('hr.employee.skill', related='user_ids.employee_skill_ids')
