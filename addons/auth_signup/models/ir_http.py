# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.technology.framework.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _pre_dispatch(cls, rule, args):
        super()._pre_dispatch(rule, args)

        # add signup token or login to the session if given
        for key in ('auth_signup_token', 'auth_login'):
            val = request.httprequest.args.get(key)
            if val is not None:
                request.session[key] = val
