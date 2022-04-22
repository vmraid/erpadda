// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

if(!window.erpadda) window.erpadda = {};

// Add / update a new Lead / Communication
// subject, sender, description
vmraid.send_message = function(opts, btn) {
	return vmraid.call({
		type: "POST",
		method: "erpadda.templates.utils.send_message",
		btn: btn,
		args: opts,
		callback: opts.callback
	});
};

erpadda.subscribe_to_newsletter = function(opts, btn) {
	return vmraid.call({
		type: "POST",
		method: "vmraid.email.doctype.newsletter.newsletter.subscribe",
		btn: btn,
		args: {"email": opts.email},
		callback: opts.callback
	});
}

// for backward compatibility
erpadda.send_message = vmraid.send_message;
