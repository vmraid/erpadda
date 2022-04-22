// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on("Program Enrollment Tool", {
	setup: function(frm) {
		frm.add_fetch("student", "title", "student_name");
		frm.add_fetch("student_applicant", "title", "student_name");
		if(frm.doc.__onload && frm.doc.__onload.academic_term_reqd) {
			frm.toggle_reqd("academic_term", true);
		}
	},

	"refresh": function(frm) {
		frm.disable_save();
		frm.fields_dict.enroll_students.$input.addClass(' btn btn-primary');
		vmraid.realtime.on("program_enrollment_tool", function(data) {
			vmraid.hide_msgprint(true);
			vmraid.show_progress(__("Enrolling students"), data.progress[0], data.progress[1]);
		});
	},

	get_students_from: function(frm) {
		if (frm.doc.get_students_from == "Student Applicant") {
			frm.dashboard.add_comment(__('Only the Student Applicant with the status "Approved" will be selected in the table below.'));
		}
	},

	"get_students": function(frm) {
		frm.set_value("students",[]);
		vmraid.call({
			method: "get_students",
			doc:frm.doc,
			callback: function(r) {
				if(r.message) {
					frm.set_value("students", r.message);
				}
			}
		});
	},

	"enroll_students": function(frm) {
		vmraid.call({
			method: "enroll_students",
			doc:frm.doc,
			callback: function(r) {
				frm.set_value("students", []);
				vmraid.hide_msgprint(true);
			}
		});
	}
});
