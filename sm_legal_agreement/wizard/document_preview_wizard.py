# -*- coding: utf-8 -*-
import re
from markupsafe import Markup
from odoo import api, fields, models, _


class DocumentPreviewWizard(models.TransientModel):
    _name = 'sm.document.preview.wizard'
    _description = 'Document Template Preview'

    template_id = fields.Many2one(
        'sm.document.template',
        string="Template",
        required=True
    )
    preview_content = fields.Html(
        string="Preview",
        compute='_compute_preview_content',
        store=True,
        sanitize=False
    )
    
    # Optional: Select a real record for preview
    record_id = fields.Integer(string="Record ID")
    use_real_record = fields.Boolean(string="Use Real Record", default=False)

    @api.depends('template_id', 'record_id', 'use_real_record')
    def _compute_preview_content(self):
        for wizard in self:
            if not wizard.template_id:
                wizard.preview_content = ""
                continue
            
            template = wizard.template_id
            content = template.template_body or ''
            
            record = None
            if wizard.use_real_record and wizard.record_id and template.model_name:
                try:
                    record = self.env[template.model_name].browse(wizard.record_id)
                    if not record.exists():
                        record = None
                except Exception:
                    record = None

            # Auto-fetch first record from model if no specific record
            if not record and template.model_name:
                try:
                    record = self.env[template.model_name].search([], limit=1)
                except Exception:
                    record = None

            if record:
                try:
                    content = template.render_template(record)
                except Exception:
                    content = self._render_with_demo(template)
            else:
                content = self._render_with_demo(template)
            
            wizard.preview_content = content

    def _render_with_demo(self, template):
        """Render template with demo/free_text values - simple replacement without extra HTML"""
        content = template.template_body or ''
        
        for var in template.variable_ids:
            if var.variable_type == 'free_text' and var.free_text_value:
                value = var.free_text_value
            else:
                value = var.demo_value or var.name
            
            # Simple replacement - no extra HTML tags
            content = content.replace(var.name, str(value))
        
        return content

    def action_print_pdf(self):
        """Generate PDF from preview using QWeb report"""
        self.ensure_one()
        return self.env.ref('sm_legal_agreement.action_report_document_template').report_action(self)
