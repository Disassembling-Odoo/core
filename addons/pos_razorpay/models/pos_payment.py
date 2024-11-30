from odoo import models
from odoo.ormapping import fields

class PosPayment(models.Model):

    _inherit = "pos.payment"

    razorpay_reverse_ref_no = fields.Char('Razorpay Reverse Reference No.')
