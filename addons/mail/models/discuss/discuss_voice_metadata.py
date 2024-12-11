# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.microkernel.ormapping import models, fields


class DiscussVoiceMetadata(models.Model):
    _name = "discuss.voice.metadata"
    _description = "Metadata for voice attachments"

    attachment_id = fields.Many2one(
        "ir.attachment", ondelete="cascade", auto_join=True, copy=False, index=True
    )
