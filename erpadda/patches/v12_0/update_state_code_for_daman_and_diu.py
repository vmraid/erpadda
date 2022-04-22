import vmraid

from erpadda.regional.india import states


def execute():

	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	# Update options in gst_state custom field
	gst_state = vmraid.get_doc("Custom Field", "Address-gst_state")
	gst_state.options = "\n".join(states)
	gst_state.save()

	# Update gst_state and state code in existing address
	vmraid.db.sql(
		"""
		UPDATE `tabAddress`
		SET
			gst_state = 'Dadra and Nagar Haveli and Daman and Diu',
			gst_state_number = 26
		WHERE gst_state = 'Daman and Diu'
	"""
	)
