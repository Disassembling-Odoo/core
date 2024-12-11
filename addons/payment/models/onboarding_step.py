# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.microkernel.api import api

class OnboardingStep(models.Model):
    _inherit = 'onboarding.onboarding.step'

    @api.model
    def action_validate_step_payment_provider(self):
        """ Override of `onboarding` to validate other steps as well. """
        return self.action_validate_step('payment.onboarding_onboarding_step_payment_provider')
