# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.api import api
from odoo.microkernel.ormapping import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_eg_building_no = fields.Char('Building No.')

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ['l10n_eg_building_no']

    def _address_fields(self):
        return super()._address_fields() + ['l10n_eg_building_no']
