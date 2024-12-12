from odoo import SUPERUSER_ID
from odoo.microkernel import api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for company in env['res.company'].search([('chart_template', '=', 'vn')], order="parent_path"):
        env['account.chart.template'].try_loading('vn', company)
