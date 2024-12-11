# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_purchase_alternatives = fields.Boolean("Purchase Alternatives", implied_group='purchase_requisition.group_purchase_alternatives')
