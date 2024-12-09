# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.microkernel.api import api
from odoo.ormapping import fields


class UomUom(models.Model):
    _inherit = 'uom.uom'

    l10n_cl_sii_code = fields.Char('SII Code')
