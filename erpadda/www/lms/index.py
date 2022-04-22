import vmraid

import erpadda.education.utils as utils

no_cache = 1


def get_context(context):
	context.education_settings = vmraid.get_single("Education Settings")
	if not context.education_settings.enable_lms:
		vmraid.local.flags.redirect_location = "/"
		raise vmraid.Redirect
	context.featured_programs = get_featured_programs()


def get_featured_programs():
	return utils.get_portal_programs() or []
