# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel import api
from odoo.microkernel.ormapping import models, fields


class PaymentCaptureWizard(models.TransientModel):
    _inherit = 'payment.capture.wizard'

    has_adyen_tx = fields.Boolean(compute='_compute_has_adyen_tx')

    @api.depends('transaction_ids')
    def _compute_has_adyen_tx(self):
        for wizard in self:
            wizard.has_adyen_tx = any(tx.provider_code == 'adyen' for tx in wizard.transaction_ids)
