// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Leave Period', {
	from_date: (frm)=>{
		if (frm.doc.from_date && !frm.doc.to_date) {
			var a_year_from_start = vmraid.datetime.add_months(frm.doc.from_date, 12);
			frm.set_value("to_date", vmraid.datetime.add_days(a_year_from_start, -1));
		}
	},
	onload: (frm) => {
		frm.set_query("department", function() {
			return {
				"filters": {
					"company": frm.doc.company,
				}
			};
		});
	},
});
