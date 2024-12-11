# -*- coding: utf-8 -*-

from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vat_check_vies = fields.Boolean(related='company_id.vat_check_vies', readonly=False,
        string='Verify VAT Numbers')
