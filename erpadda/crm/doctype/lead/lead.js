// Copyright (c) 2019, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.provide("erpadda");
cur_frm.email_field = "email_id";

erpadda.LeadController = class LeadController extends vmraid.ui.form.Controller {
	setup () {
		this.frm.make_methods = {
			'Customer': this.make_customer,
			'Quotation': this.make_quotation,
			'Opportunity': this.make_opportunity
		};

		// For avoiding integration issues.
		this.frm.set_df_property('first_name', 'reqd', true);
	}

	onload () {
		this.frm.set_query("customer", function (doc, cdt, cdn) {
			return { query: "erpadda.controllers.queries.customer_query" }
		});

		this.frm.set_query("lead_owner", function (doc, cdt, cdn) {
			return { query: "vmraid.core.doctype.user.user.user_query" }
		});

		this.frm.set_query("contact_by", function (doc, cdt, cdn) {
			return { query: "vmraid.core.doctype.user.user.user_query" }
		});
	}

	refresh () {
		let doc = this.frm.doc;
		erpadda.toggle_naming_series();
		vmraid.dynamic_link = { doc: doc, fieldname: 'name', doctype: 'Lead' }

		if (!this.frm.is_new() && doc.__onload && !doc.__onload.is_customer) {
			this.frm.add_custom_button(__("Customer"), this.make_customer, __("Create"));
			this.frm.add_custom_button(__("Opportunity"), this.make_opportunity, __("Create"));
			this.frm.add_custom_button(__("Quotation"), this.make_quotation, __("Create"));
			this.frm.add_custom_button(__("Prospect"), this.make_prospect, __("Create"));
			this.frm.add_custom_button(__('Add to Prospect'), this.add_lead_to_prospect, __('Action'));
		}

		if (!this.frm.is_new()) {
			vmraid.contacts.render_address_and_contact(this.frm);
			cur_frm.trigger('render_contact_day_html');
		} else {
			vmraid.contacts.clear_address_and_contact(this.frm);
		}
	}

	add_lead_to_prospect () {
		vmraid.prompt([
			{
				fieldname: 'prospect',
				label: __('Prospect'),
				fieldtype: 'Link',
				options: 'Prospect',
				reqd: 1
			}
		],
		function(data) {
			vmraid.call({
				method: 'erpadda.crm.doctype.lead.lead.add_lead_to_prospect',
				args: {
					'lead': cur_frm.doc.name,
					'prospect': data.prospect
				},
				callback: function(r) {
					if (!r.exc) {
						frm.reload_doc();
					}
				},
				freeze: true,
				freeze_message: __('...Adding Lead to Prospect')
			});
		}, __('Add Lead to Prospect'), __('Add'));
	}

	make_customer () {
		vmraid.model.open_mapped_doc({
			method: "erpadda.crm.doctype.lead.lead.make_customer",
			frm: cur_frm
		})
	}

	make_opportunity () {
		vmraid.model.open_mapped_doc({
			method: "erpadda.crm.doctype.lead.lead.make_opportunity",
			frm: cur_frm
		})
	}

	make_quotation () {
		vmraid.model.open_mapped_doc({
			method: "erpadda.crm.doctype.lead.lead.make_quotation",
			frm: cur_frm
		})
	}

	make_prospect () {
		vmraid.model.with_doctype("Prospect", function() {
			let prospect = vmraid.model.get_new_doc("Prospect");
			prospect.company_name = cur_frm.doc.company_name;
			prospect.no_of_employees = cur_frm.doc.no_of_employees;
			prospect.industry = cur_frm.doc.industry;
			prospect.market_segment = cur_frm.doc.market_segment;
			prospect.territory = cur_frm.doc.territory;
			prospect.fax = cur_frm.doc.fax;
			prospect.website = cur_frm.doc.website;
			prospect.prospect_owner = cur_frm.doc.lead_owner;

			let lead_prospect_row = vmraid.model.add_child(prospect, 'prospect_lead');
			lead_prospect_row.lead = cur_frm.doc.name;

			vmraid.set_route("Form", "Prospect", prospect.name);
		});
	}

	company_name () {
		if (!this.frm.doc.lead_name) {
			this.frm.set_value("lead_name", this.frm.doc.company_name);
		}
	}

	contact_date () {
		if (this.frm.doc.contact_date) {
			let d = moment(this.frm.doc.contact_date);
			d.add(1, "day");
			this.frm.set_value("ends_on", d.format(vmraid.defaultDatetimeFormat));
		}
	}

	render_contact_day_html() {
		if (cur_frm.doc.contact_date) {
			let contact_date = vmraid.datetime.obj_to_str(cur_frm.doc.contact_date);
			let diff_days = vmraid.datetime.get_day_diff(contact_date, vmraid.datetime.get_today());
			let color = diff_days > 0 ? "orange" : "green";
			let message = diff_days > 0 ? __("Next Contact Date") : __("Last Contact Date");
			let html = `<div class="col-xs-12">
						<span class="indicator whitespace-nowrap ${color}"><span> ${message} : ${vmraid.datetime.global_date_format(contact_date)}</span></span>
					</div>` ;
			cur_frm.dashboard.set_headline_alert(html);
		}
	}
};

extend_cscript(cur_frm.cscript, new erpadda.LeadController({ frm: cur_frm }));
