// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

{% include 'erpadda/loan_management/loan_common.js' %};

vmraid.ui.form.on('Loan Disbursement', {
	refresh: function(frm) {
		frm.set_query('against_loan', function() {
			return {
				'filters': {
					'docstatus': 1,
					'status': 'Sanctioned'
				}
			}
		})
	}
});
