vmraid.ui.form.on("Journal Entry", {
	refresh: function(frm) {
		frm.set_query('company_address', function(doc) {
			if(!doc.company) {
				vmraid.throw(__('Please set Company'));
			}

			return {
				query: 'vmraid.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Company',
					link_name: doc.company
				}
			};
		});
	}
});
