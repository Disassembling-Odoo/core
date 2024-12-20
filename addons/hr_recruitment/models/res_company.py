# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    candidate_properties_definition = fields.PropertiesDefinition('Candidate Properties')
    job_properties_definition = fields.PropertiesDefinition("Job Properties")
