// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on("Student Applicant", {
	setup: function(frm) {
		frm.add_fetch("guardian", "guardian_name", "guardian_name");
	},

	refresh: function(frm) {
		if (frm.doc.application_status==="Applied" && frm.doc.docstatus===1 ) {
			frm.add_custom_button(__("Approve"), function() {
				frm.set_value("application_status", "Approved");
				frm.save_or_update();

			}, 'Actions');

			frm.add_custom_button(__("Reject"), function() {
				frm.set_value("application_status", "Rejected");
				frm.save_or_update();
			}, 'Actions');
		}

		if (frm.doc.application_status === "Approved" && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Enroll"), function() {
				frm.events.enroll(frm)
			}).addClass("btn-primary");

			frm.add_custom_button(__("Reject"), function() {
				frm.set_value("application_status", "Rejected");
				frm.save_or_update();
			}, 'Actions');
		}

		vmraid.realtime.on("enroll_student_progress", function(data) {
			if(data.progress) {
				vmraid.hide_msgprint(true);
				vmraid.show_progress(__("Enrolling student"), data.progress[0],data.progress[1]);
			}
		});

		vmraid.db.get_value("Education Settings", {name: "Education Settings"}, "user_creation_skip", (r) => {
			if (cint(r.user_creation_skip) !== 1) {
				frm.set_df_property("student_email_id", "reqd", 1);
			}
		});
	},

	enroll: function(frm) {
		vmraid.model.open_mapped_doc({
			method: "erpadda.education.api.enroll_student",
			frm: frm
		})
	}
});

vmraid.ui.form.on('Student Sibling', {
	setup: function(frm) {
		frm.add_fetch("student", "title", "full_name");
		frm.add_fetch("student", "gender", "gender");
		frm.add_fetch("student", "date_of_birth", "date_of_birth");
	}
});
