# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.microkernel.api import api
from odoo.ormapping import fields


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    adyen_merchant_account = fields.Char(help='The POS merchant account code used in Adyen')

    def _get_adyen_endpoints(self):
        return {
            **super(PosPaymentMethod, self)._get_adyen_endpoints(),
            'adjust': 'https://pal-%s.adyen.com/pal/servlet/Payment/v52/adjustAuthorisation',
            'capture': 'https://pal-%s.adyen.com/pal/servlet/Payment/v52/capture',
        }

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['adyen_merchant_account']
        return params
