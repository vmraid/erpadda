// Copyright (c) 2020, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Video', {
	refresh: function (frm) {
		frm.events.toggle_youtube_statistics_section(frm);
		frm.add_custom_button(__("Watch Video"), () => vmraid.help.show_video(frm.doc.url, frm.doc.title));
	},

	toggle_youtube_statistics_section: (frm) => {
		if (frm.doc.provider === "YouTube") {
			vmraid.db.get_single_value("Video Settings", "enable_youtube_tracking").then( val => {
				frm.toggle_display("youtube_tracking_section", val);
			});
		}
	}
});
