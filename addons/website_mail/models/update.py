# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.microkernel import api

class PublisherWarrantyContract(models.AbstractModel):
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message(self):
        msg = super(PublisherWarrantyContract, self)._get_message()
        msg['website'] = True
        return msg
