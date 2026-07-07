# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Document Template Builder',
    'version': '16.0.1.0.1',
    'category': 'Productivity',
    'summary': 'Create dynamic document templates with placeholders mapped to any model fields',
    'description': """
Dynamic Document Template Builder
=================================

This module allows you to create dynamic document templates with customizable placeholders 
that can be mapped to any Odoo model fields or free text values.

Key Features:
-------------
* Create unlimited document templates with HTML editor
* Use dynamic placeholders like {{1}}, {{2}}, {{3}}...
* Map placeholders to any field from any Odoo model
* Or use free text values for static content
* Live preview with demo values
* Generate PDF reports from templates
* Multi-company support
* Easy to use interface

Use Cases:
----------
* Legal agreements and contracts
* Employment letters
* Invoice cover letters
* Custom quotation templates
* Any document that needs dynamic content

How to Use:
-----------
1. Create a new template
2. Write your document content using {{1}}, {{2}}, etc. for dynamic parts
3. In the Variables tab, configure each placeholder:
   - Choose "Free Text" for static values
   - Choose "Field of Model" to link to a model field
4. Use Preview to see how it looks with demo values
5. Link the template to your records and generate documents
    """,
    'author': 'Steven Marp',
    'website': 'https://apps.odoo.com/apps/browse?repo_maintainer_id=512936',
    'license': 'OPL-1',
    'price': 400.00,
    'currency': 'USD',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'report/document_template_report.xml',
        'views/document_template_views.xml',
        'wizard/document_preview_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sm_legal_agreement/static/src/js/dynamic_field_selector.js',
            'sm_legal_agreement/static/src/xml/dynamic_field_selector.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
