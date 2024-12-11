# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project')
