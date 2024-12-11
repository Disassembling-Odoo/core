# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _mailing_enabled = True
