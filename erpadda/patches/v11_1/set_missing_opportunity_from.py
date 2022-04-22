import vmraid


def execute():

	vmraid.reload_doctype("Opportunity")
	if vmraid.db.has_column("Opportunity", "enquiry_from"):
		vmraid.db.sql(
			""" UPDATE `tabOpportunity` set opportunity_from = enquiry_from
			where ifnull(opportunity_from, '') = '' and ifnull(enquiry_from, '') != ''"""
		)

	if vmraid.db.has_column("Opportunity", "lead") and vmraid.db.has_column(
		"Opportunity", "enquiry_from"
	):
		vmraid.db.sql(
			""" UPDATE `tabOpportunity` set party_name = lead
			where enquiry_from = 'Lead' and ifnull(party_name, '') = '' and ifnull(lead, '') != ''"""
		)

	if vmraid.db.has_column("Opportunity", "customer") and vmraid.db.has_column(
		"Opportunity", "enquiry_from"
	):
		vmraid.db.sql(
			""" UPDATE `tabOpportunity` set party_name = customer
			 where enquiry_from = 'Customer' and ifnull(party_name, '') = '' and ifnull(customer, '') != ''"""
		)
