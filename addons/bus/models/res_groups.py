# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models

class ResGroups(models.Model):
    _name = "res.groups"
    _inherit = ["res.groups", "bus.listener.mixin"]
