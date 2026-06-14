/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useService } from "@web/core/utils/hooks";
import { useState, useRef, onMounted } from "@odoo/owl";

/**
 * Dynamic Field Selector Widget
 * Provides autocomplete suggestions for model field paths
 */
export class DynamicFieldSelectorChar extends CharField {
    static template = "sm_legal_agreement.DynamicFieldSelectorChar";
    static props = {
        ...CharField.props,
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            suggestions: [],
            showSuggestions: false,
            loading: false,
        });
        this.inputRef = useRef("input");
    }

    get modelName() {
        // Get model name from the record's model_name field
        return this.props.record.data.model_name || "";
    }

    async onInput(ev) {
        const value = ev.target.value;
        await this.props.record.update({ [this.props.name]: value });
        
        if (value && this.modelName) {
            await this.fetchFieldSuggestions(value);
        } else {
            this.state.suggestions = [];
            this.state.showSuggestions = false;
        }
    }

    async fetchFieldSuggestions(query) {
        if (!this.modelName) return;
        
        this.state.loading = true;
        try {
            // Get fields from the model
            const fields = await this.orm.call(
                "ir.model.fields",
                "search_read",
                [[
                    ["model", "=", this.modelName],
                    ["name", "ilike", query.split(".").pop()],
                    ["ttype", "not in", ["one2many", "many2many", "binary"]]
                ]],
                { fields: ["name", "field_description", "ttype", "relation"], limit: 10 }
            );

            this.state.suggestions = fields.map(f => ({
                name: this.buildFieldPath(query, f.name),
                label: f.field_description,
                type: f.ttype,
                relation: f.relation,
            }));
            this.state.showSuggestions = this.state.suggestions.length > 0;
        } catch (e) {
            console.warn("Error fetching field suggestions:", e);
            this.state.suggestions = [];
        }
        this.state.loading = false;
    }

    buildFieldPath(currentPath, fieldName) {
        const parts = currentPath.split(".");
        parts.pop();
        parts.push(fieldName);
        return parts.join(".");
    }

    async selectSuggestion(suggestion) {
        await this.props.record.update({ [this.props.name]: suggestion.name });
        this.state.showSuggestions = false;
        
        // If it's a relational field, allow further drilling
        if (suggestion.relation) {
            // Could show more suggestions here
        }
    }

    onBlur() {
        // Delay hiding to allow click on suggestion
        setTimeout(() => {
            this.state.showSuggestions = false;
        }, 200);
    }

    onFocus() {
        if (this.state.suggestions.length > 0) {
            this.state.showSuggestions = true;
        }
    }
}

export const dynamicFieldSelectorChar = {
    ...charField,
    component: DynamicFieldSelectorChar,
};

registry.category("fields").add("DynamicFieldSelectorChar", dynamicFieldSelectorChar);
