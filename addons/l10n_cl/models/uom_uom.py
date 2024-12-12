# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.microkernel import api
from odoo.microkernel.ormapping import models, fields


class UomUom(models.Model):
    _inherit = 'uom.uom'

    l10n_cl_sii_code = fields.Char('SII Code')
