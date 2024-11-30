from odoo import models
from odoo.ormapping import fields

class ModelMultiCompany(models.Model):
    _name = "test.model_multicompany"
    _description = "test multicompany model"

    name = fields.Char()
    company_id = fields.Many2one("res.company")
