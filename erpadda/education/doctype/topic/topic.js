// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Topic', {
	refresh: function(frm) {
		if (!cur_frm.doc.__islocal) {
			frm.add_custom_button(__('Add to Courses'), function() {
				frm.trigger('add_topic_to_courses');
			}, __('Action'));
		}
	},

	add_topic_to_courses: function(frm) {
		get_courses_without_topic(frm.doc.name).then(r => {
			if (r.message.length) {
				vmraid.prompt([
					{
						fieldname: 'courses',
						label: __('Courses'),
						fieldtype: 'MultiSelectPills',
						get_data: function() {
							return r.message;
						}
					}
				],
				function(data) {
					vmraid.call({
						method: 'erpadda.education.doctype.topic.topic.add_topic_to_courses',
						args: {
							'topic': frm.doc.name,
							'courses': data.courses
						},
						callback: function(r) {
							if (!r.exc) {
								frm.reload_doc();
							}
						},
						freeze: true,
						freeze_message: __('...Adding Topic to Courses')
					});
				}, __('Add Topic to Courses'), __('Add'));
			} else {
				vmraid.msgprint(__('This topic is already added to the existing courses'));
			}
		});
	}
});

let get_courses_without_topic = function(topic) {
	return vmraid.call({
		type: 'GET',
		method: 'erpadda.education.doctype.topic.topic.get_courses_without_topic',
		args: {'topic': topic}
	});
};
