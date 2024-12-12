# -*- coding: utf-8 -*-

from odoo.microkernel import api
from odoo.microkernel.ormapping import models, fields


class ResUsersLog(models.Model):
    _inherit = 'res.users.log'

    create_uid = fields.Integer(index=True)
    ip = fields.Char(string="IP Address")
