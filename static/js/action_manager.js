/** @odoo-module **/

import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";

registry
    .category("ir.actions.report handlers")
    .add("xlsx_handler", async function (action, options, env) {
        if (action.report_type === "xlsx") {
       framework.blockUI();
       var def = $.Deferred();
       session.get_file({
           url: '/xlsx_reports',
           data: action.data,
           success: def.resolve.bind(def),
           error: (error) => this.call('crash_manager', 'rpc_error', error),
           complete: framework.unblockUI,
       });
       return def;
   }
});
