# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel import api
from odoo.microkernel.ormapping import models, fields


class MailTestCC(models.Model):
    _name = 'mail.test.cc'
    _description = "Test Email CC Thread"
    _inherit = ['mail.thread.cc']

    name = fields.Char()
