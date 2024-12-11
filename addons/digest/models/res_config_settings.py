# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    digest_emails = fields.Boolean(string="Digest Emails", config_parameter='digest.default_digest_emails')
    digest_id = fields.Many2one('digest.digest', string='Digest Email', config_parameter='digest.default_digest_id')
