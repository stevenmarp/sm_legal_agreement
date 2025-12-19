# Dynamic Document Template Builder

Create dynamic document templates with customizable placeholders that can be mapped to any Odoo model fields.

## Features

- 📝 **Rich HTML Editor** - Create beautiful documents with formatting
- 🔄 **Dynamic Placeholders** - Use `{{1}}`, `{{2}}`, `{{3}}` for dynamic content
- 🔗 **Model Field Mapping** - Link placeholders to any field from any model
- ✏️ **Free Text Values** - Or use static text values
- 👁️ **Live Preview** - See how your document looks with demo values
- 🏢 **Multi-Company** - Support for multi-company environments
- 🌍 **Translatable** - Templates can be translated

## Installation

1. Download the module
2. Place it in your Odoo addons directory
3. Update the apps list
4. Install "Dynamic Document Template Builder"

## Usage

### Creating a Template

1. Go to **Document Templates** > **Templates**
2. Click **Create**
3. Enter a name and select the source model
4. Write your template content using placeholders

### Using Placeholders

Use `{{1}}`, `{{2}}`, `{{3}}`, etc. as placeholders:

```
Dear {{1}},

Thank you for your order #{{2}} dated {{3}}.
The total amount is {{4}}.

Best regards,
{{5}}
```

### Configuring Variables

In the **Variables** tab, configure each placeholder:

| Placeholder | Type | Value |
|-------------|------|-------|
| {{1}} | Model Field | `partner_id.name` |
| {{2}} | Model Field | `name` |
| {{3}} | Model Field | `date_order` |
| {{4}} | Model Field | `amount_total` |
| {{5}} | Free Text | `Sales Team` |

### Field Path Examples

- `name` - Direct field
- `partner_id.name` - Related field (Many2one)
- `partner_id.country_id.name` - Nested relation
- `amount_total` - Numeric field
- `state` - Selection field

## API Usage

```python
# Get template
template = env['sm.document.template'].browse(template_id)

# Render with a record
sale_order = env['sale.order'].browse(order_id)
rendered_html = template.render_template(sale_order)
```

## Support

For support, customization, or feature requests, please contact:
- Email: support@example.com

## License

This module is licensed under LGPL-3.

## Changelog

### 18.0.1.0.0
- Initial release
- Support for any Odoo model
- Dynamic placeholder detection
- Field path support with dot notation
- Live preview functionality
