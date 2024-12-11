# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    flutterwave_customer_email = fields.Char(
        help="The email of the customer at the time the token was created.", readonly=True
    )
