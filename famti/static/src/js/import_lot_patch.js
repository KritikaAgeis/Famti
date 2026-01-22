// /** @odoo-module **/
//
// import { patch } from "@web/core/utils/patch";
// import { GenerateSerialDialog } from "@stock/components/generate_serial_dialog/generate_serial_dialog";
// import { useService } from "@web/core/utils/hooks";
//
// patch(GenerateSerialDialog.prototype, {
//     setup() {
//         console.log("-------------------------------------");
//         super.setup();
//         this.actionService = useService("action");
//     },
//
//     openExcelImport() {
//                     console.log("-------------------oepn wizard------------------");
//         this.actionService.doAction({
//             type: "ir.actions.act_window",
//             res_model: "famti.lot.import.wizard",
//             name: "Import Lots from Excel",
//             view_mode: "form",
//             target: "new",
//             context: {
//                 active_id: this.props.move.id,
//                 active_model: "stock.move",
//             },
//         });
//     },
// });

/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { GenerateSerialDialog } from "@stock/views/generate_serial_dialog/generate_serial_dialog";

patch(GenerateSerialDialog.prototype, {

    openExcelImport() {
        console.log("Excel / CSV upload button clicked");

        // Example: open file selector
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".xls,.xlsx,.csv";
        input.click();

        input.onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                console.log("Selected file:", file.name);

                // TODO:
                // - Read file (FileReader)
                // - Parse CSV / Excel
                // - Send to backend via RPC
            }
        };
    },

});
