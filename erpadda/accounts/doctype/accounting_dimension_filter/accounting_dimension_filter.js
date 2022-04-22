// Copyright (c) 2020, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Accounting Dimension Filter', {
	refresh: function(frm, cdt, cdn) {
		if (frm.doc.accounting_dimension) {
			frm.set_df_property('dimensions', 'label', frm.doc.accounting_dimension, cdn, 'dimension_value');
		}

		let help_content =
			`<table class="table table-bordered" style="background-color: var(--scrollbar-track-color);">
				<tr><td>
					<p>
						<i class="fa fa-hand-right"></i>
						{{__('Note: On checking Is Mandatory the accounting dimension will become mandatory against that specific account for all accounting transactions')}}
					</p>
				</td></tr>
			</table>`;

		frm.set_df_property('dimension_filter_help', 'options', help_content);
	},
	onload: function(frm) {
		frm.set_query('applicable_on_account', 'accounts', function() {
			return {
				filters: {
					'company': frm.doc.company
				}
			};
		});

		vmraid.db.get_list('Accounting Dimension',
			{fields: ['document_type']}).then((res) => {
			let options = ['Cost Center', 'Project'];

			res.forEach((dimension) => {
				options.push(dimension.document_type);
			});

			frm.set_df_property('accounting_dimension', 'options', options);
		});

		frm.trigger('setup_filters');
	},

	setup_filters: function(frm) {
		let filters = {};

		if (frm.doc.accounting_dimension) {
			vmraid.model.with_doctype(frm.doc.accounting_dimension, function() {
				if (vmraid.model.is_tree(frm.doc.accounting_dimension)) {
					filters['is_group'] = 0;
				}

				if (vmraid.meta.has_field(frm.doc.accounting_dimension, 'company')) {
					filters['company'] = frm.doc.company;
				}

				frm.set_query('dimension_value', 'dimensions', function() {
					return {
						filters: filters
					};
				});
			});
		}
	},

	accounting_dimension: function(frm) {
		frm.clear_table("dimensions");
		let row = frm.add_child("dimensions");
		row.accounting_dimension = frm.doc.accounting_dimension;
		frm.refresh_field("dimensions");
		frm.trigger('setup_filters');
	},
});

vmraid.ui.form.on('Allowed Dimension', {
	dimensions_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.accounting_dimension = frm.doc.accounting_dimension;
		frm.refresh_field("dimensions");
	}
});
