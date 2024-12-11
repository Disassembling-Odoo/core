# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    project_id = fields.Many2one('project.project')
