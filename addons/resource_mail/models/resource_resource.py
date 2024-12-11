# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    im_status = fields.Char(related='user_id.im_status')
