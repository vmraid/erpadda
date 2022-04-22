// Copyright (c) 2019, VMRaid and Contributors
// MIT License. See license.txt

vmraid.ui.form.on('Website Theme', {
	validate(frm) {
		let theme_scss = frm.doc.theme_scss;
		if (theme_scss && theme_scss.includes('vmraid/public/scss/website')
			&& !theme_scss.includes('erpadda/public/scss/website')
		) {
			frm.set_value('theme_scss',
				`${frm.doc.theme_scss}\n@import "erpadda/public/scss/website";`);
		}
	}
});
