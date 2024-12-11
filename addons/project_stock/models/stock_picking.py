# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project')
