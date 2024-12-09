from odoo import SUPERUSER_ID
from odoo.microkernel.api import api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for company in env['res.company'].search([('chart_template', '=', 'se')], order="parent_path"):
        env['account.chart.template'].try_loading('se', company)
