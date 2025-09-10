/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class VatDynamicLabel extends CharField {
    setup() {
        super.setup();

        // Observar cambios en company_type
        this.props.record.onChange("company_type", this._onCompanyTypeChange.bind(this));
    }

    _onCompanyTypeChange() {
        const companyType = this.props.record.data.company_type;
        this._updateLabel(companyType);
    }

    _updateLabel(companyType) {
        const labelElement = this.el?.closest(".o_field_widget")?.previousElementSibling;
        if (labelElement && labelElement.tagName === "LABEL") {
            labelElement.textContent = companyType === "company" ? "RNC" : "Cédula";
        }
    }

    onMounted() {
        super.onMounted();
        this._updateLabel(this.props.record.data.company_type);
    }
}

registry.category("fields").add("vat_dynamic_label", VatDynamicLabel);
