odoo.define('sm_legal_agreement.DynamicFieldSelectorChar', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var core = require('web.core');

    var DynamicFieldSelectorChar = AbstractField.extend({
        template: 'DynamicFieldSelectorChar',
        events: {
            'input input': '_onInput',
            'blur input': '_onBlur',
            'focus input': '_onFocus',
            'click .o_suggestion_item': '_onClickSuggestion',
        },
        init: function () {
            this._super.apply(this, arguments);
            this.suggestions = [];
            this.showSuggestions = false;
            this.loading = false;
        },
        _renderEdit: function () {
            var self = this;
            this.$el.html(core.qweb.render('DynamicFieldSelectorChar.edit', {
                value: this.value || '',
                placeholder: this.attrs.placeholder || 'e.g. partner_id.name',
                suggestions: this.suggestions,
                showSuggestions: this.showSuggestions,
                loading: this.loading,
            }));
            this.$input = this.$('input');
        },
        _renderReadonly: function () {
            this.$el.text(this.value || '');
        },
        _getRecordData: function () {
            var record = this.recordData;
            return record.model_name || '';
        },
        _onInput: function (ev) {
            var self = this;
            var value = $(ev.currentTarget).val();
            this._setValue(value);
            
            var modelName = this._getRecordData();
            if (value && modelName) {
                this.loading = true;
                this._renderEdit();
                
                var queryField = value.split('.').pop();
                this._rpc({
                    model: 'ir.model.fields',
                    method: 'search_read',
                    args: [[
                        ['model', '=', modelName],
                        ['name', 'ilike', queryField],
                        ['ttype', 'not in', ['one2many', 'many2many', 'binary']]
                    ]],
                    kwargs: {
                        fields: ['name', 'field_description', 'ttype', 'relation'],
                        limit: 10
                    }
                }).then(function (fields) {
                    self.suggestions = _.map(fields, function (f) {
                        return {
                            name: self._buildFieldPath(value, f.name),
                            label: f.field_description,
                            type: f.ttype,
                            relation: f.relation,
                        };
                    });
                    self.showSuggestions = self.suggestions.length > 0;
                    self.loading = false;
                    self._renderEdit();
                }, function () {
                    self.loading = false;
                    self._renderEdit();
                });
            } else {
                this.suggestions = [];
                this.showSuggestions = false;
                this._renderEdit();
            }
        },
        _buildFieldPath: function (currentPath, fieldName) {
            var parts = currentPath.split('.');
            parts.pop();
            parts.push(fieldName);
            return parts.join('.');
        },
        _onClickSuggestion: function (ev) {
            var suggestionName = $(ev.currentTarget).data('name');
            this._setValue(suggestionName);
            this.showSuggestions = false;
            this._renderEdit();
        },
        _onBlur: function () {
            var self = this;
            setTimeout(function () {
                self.showSuggestions = false;
                self._renderEdit();
            }, 200);
        },
        _onFocus: function () {
            if (this.suggestions.length > 0) {
                this.showSuggestions = true;
                this._renderEdit();
            }
        },
    });

    field_registry.add('DynamicFieldSelectorChar', DynamicFieldSelectorChar);

    return DynamicFieldSelectorChar;
});
