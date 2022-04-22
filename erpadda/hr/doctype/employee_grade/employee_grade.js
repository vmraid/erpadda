// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Employee Grade', {
    refresh: function (frm) {

    },
    setup: function (frm) {
        frm.set_query("default_salary_structure", function () {
            return {
                "filters": {
                    "docstatus": 1,
                    "is_active": "Yes"
                }
            };
        });

        frm.set_query("default_leave_policy", function () {
            return {
                "filters": {
                    "docstatus": 1
                }
            };
        });


    }

});
