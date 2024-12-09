# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.microkernel.api import api
from odoo.ormapping import fields


class Product(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(help='Check if the product is eligible for membership.')
    membership_date_from = fields.Date(string='Membership Start Date',
        help='Date from which membership becomes active.')
    membership_date_to = fields.Date(string='Membership End Date',
        help='Date until which membership remains active.')

    _sql_constraints = [
        ('membership_date_greater', 'check(membership_date_to >= membership_date_from)', 'Error! Ending Date cannot be set before Beginning Date.')
    ]
