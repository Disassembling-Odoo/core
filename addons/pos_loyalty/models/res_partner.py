from odoo.microkernel.ormapping import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_card_count = fields.Integer(groups='base.group_user,point_of_sale.group_pos_user')
