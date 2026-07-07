# -*- coding: utf-8 -*-
import re
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DocumentTemplate(models.Model):
    _name = 'sm.document.template'
    _description = 'Dynamic Document Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char(
        string="Template Name",
        required=True,
        tracking=True,
        translate=True
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, tracking=True)
    
    # Template Configuration
    model_id = fields.Many2one(
        'ir.model',
        string="Source Model",
        required=True,
        ondelete='cascade',
        tracking=True,
        domain=[('transient', '=', False)],
        help="Select the model from which this template will get its data"
    )
    model_name = fields.Char(
        related='model_id.model',
        string="Model Name",
        store=True
    )
    
    # Template Content
    template_body = fields.Html(
        string="Template Content",
        required=True,
        translate=True,
        sanitize=False,
        help="Use {{1}}, {{2}}, {{3}}... as placeholders for dynamic content"
    )
    
    # Generated Preview
    preview_body = fields.Html(
        string="Preview",
        compute='_compute_preview_body',
        sanitize=False
    )
    
    # Variables
    variable_ids = fields.One2many(
        'sm.document.template.variable',
        'template_id',
        string="Template Variables",
        compute='_compute_variable_ids',
        store=True,
        readonly=False,
        copy=True
    )
    
    # Categorization
    category = fields.Selection([
        ('legal', 'Legal Agreement'),
        ('contract', 'Contract'),
        ('letter', 'Letter'),
        ('report', 'Report'),
        ('other', 'Other')
    ], string="Category", default='other', tracking=True)
    
    description = fields.Text(string="Description", translate=True)
    
    # Multi-company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        tracking=True
    )
    
    # Statistics
    usage_count = fields.Integer(
        string="Usage Count",
        default=0,
        readonly=True
    )

    @api.depends('template_body')
    def _compute_variable_ids(self):
        """Auto-detect placeholders in template and create/update variables"""
        for rec in self:
            if not rec.template_body:
                continue
                
            # Find all placeholders like {{1}}, {{2}}, {{10}}, etc.
            body_vars = set(re.findall(r'\{\{[1-9][0-9]*\}\}', rec.template_body or ''))
            existing_vars = rec.variable_ids
            existing_names = set(existing_vars.mapped('name'))
            
            # Variables to create
            new_vars = [name for name in body_vars if name not in existing_names]
            
            # Variables to delete (no longer in template)
            vars_to_delete = existing_vars.filtered(lambda v: v.name not in body_vars)
            
            # Build commands
            commands = []
            for var in vars_to_delete:
                commands.append((2, var.id))
            for name in sorted(new_vars, key=lambda x: int(x.strip('{}'))):
                commands.append((0, 0, {'name': name}))
            
            if commands:
                rec.variable_ids = commands

    @api.depends('template_body', 'variable_ids.demo_value', 'variable_ids.free_text_value')
    def _compute_preview_body(self):
        """Generate preview with demo values"""
        for rec in self:
            if not rec.template_body:
                rec.preview_body = ""
                continue
                
            preview = rec.template_body
            for var in rec.variable_ids:
                # Use free_text_value if type is free_text, otherwise use demo_value
                if var.variable_type == 'free_text' and var.free_text_value:
                    value = var.free_text_value
                else:
                    value = var.demo_value or var.name
                # Simple replacement without extra HTML - the template already has styling
                preview = preview.replace(var.name, str(value))
            
            rec.preview_body = preview

    def action_preview(self):
        """Open preview wizard"""
        self.ensure_one()
        return {
            'name': _('Preview Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'sm.document.preview.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
            }
        }

    def action_print_pdf(self):
        """Print template directly as PDF (with demo values)"""
        self.ensure_one()
        # Create a wizard record for report generation
        wizard = self.env['sm.document.preview.wizard'].create({
            'template_id': self.id,
        })
        return self.env.ref('sm_legal_agreement.action_report_document_template').report_action(wizard)

    def render_template(self, record):
        """
        Render the template with actual values from a record
        
        :param record: recordset of the source model
        :return: rendered HTML content
        """
        self.ensure_one()
        
        if not record:
            raise UserError(_("No record provided for rendering template."))
        
        if record._name != self.model_name:
            raise UserError(_(
                "Record model '%(record_model)s' does not match template model '%(template_model)s'.",
                record_model=record._name,
                template_model=self.model_name
            ))
        
        rendered = self.template_body or ''
        
        for var in self.variable_ids:
            if var.variable_type == 'free_text':
                value = var.free_text_value or ''
            elif var.variable_type == 'field':
                value = self._get_field_value(record, var.field_path)
            else:
                value = var.demo_value or ''
            
            rendered = rendered.replace(var.name, str(value))
        
        # Increment usage count
        self.sudo().usage_count += 1
        
        return rendered

    def _get_field_value(self, record, field_path):
        """
        Get field value from record using dot notation path
        
        :param record: recordset
        :param field_path: string like 'partner_id.name' or 'amount_total'
        :return: field value as string
        """
        if not field_path:
            return ''
        
        try:
            value = record
            for field_name in field_path.split('.'):
                if hasattr(value, field_name):
                    value = getattr(value, field_name)
                else:
                    return ''
            
            # Format different types
            if isinstance(value, models.Model):
                return value.display_name if value else ''
            elif isinstance(value, (list, tuple)):
                return ', '.join(str(v) for v in value)
            elif value is False:
                return ''
            else:
                return str(value)
        except Exception as e:
            _logger.warning("Error getting field value for path '%s': %s", field_path, e)
            return ''

    @api.model
    def get_available_models(self):
        """Return list of models that can be used as source"""
        models = self.env['ir.model'].search([
            ('transient', '=', False),
            ('model', 'not like', 'ir.%'),
            ('model', 'not like', 'res.config%'),
        ], order='name')
        return [(m.model, m.name) for m in models]


class DocumentTemplateVariable(models.Model):
    _name = 'sm.document.template.variable'
    _description = 'Document Template Variable'
    _order = 'name'

    template_id = fields.Many2one(
        'sm.document.template',
        string="Template",
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string="Placeholder",
        required=True,
        help="The placeholder name like {{1}}, {{2}}, etc."
    )
    
    # Variable Type
    variable_type = fields.Selection([
        ('free_text', 'Free Text'),
        ('field', 'Model Field')
    ], string="Type", required=True, default='free_text')
    
    # For Free Text
    free_text_value = fields.Char(
        string="Text Value",
        help="Enter a static text value"
    )
    
    # For Field
    field_path = fields.Char(
        string="Field Path",
        help="Enter the field path like 'name', 'partner_id.name', 'amount_total'"
    )
    model_name = fields.Char(
        related='template_id.model_name',
        string="Model"
    )
    
    # Demo value for preview
    demo_value = fields.Char(
        string="Demo Value",
        default="[Demo]",
        help="Value shown in preview mode"
    )

    @api.onchange('variable_type')
    def _onchange_variable_type(self):
        """Clear values when type changes"""
        if self.variable_type == 'free_text':
            self.field_path = False
        else:
            self.free_text_value = False

    @api.onchange('field_path')
    def _onchange_field_path(self):
        """Update demo value based on field"""
        if self.field_path and self.variable_type == 'field':
            self.demo_value = f"[{self.field_path}]"
