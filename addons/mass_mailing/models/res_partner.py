# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models

class Partner(models.Model):
    _inherit = 'res.partner'
    _mailing_enabled = True
