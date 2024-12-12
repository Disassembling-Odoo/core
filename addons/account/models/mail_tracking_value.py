# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.microkernel.ormapping import models
from odoo.microkernel import api


class MailTrackingValues(models.Model):
    _inherit = 'mail.tracking.value'

    @api.ondelete(at_uninstall=True)
    def _except_audit_log(self):
        self.mail_message_id._except_audit_log()

    def write(self, vals):
        self._except_audit_log()
        return super().write(vals)
