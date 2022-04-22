import vmraid
from vmraid import _

import erpadda.education.utils as utils

no_cache = 1


def get_context(context):
	try:
		program = vmraid.form_dict["program"]
	except KeyError:
		vmraid.local.flags.redirect_location = "/lms"
		raise vmraid.Redirect

	context.education_settings = vmraid.get_single("Education Settings")
	context.program = get_program(program)
	context.courses = [vmraid.get_doc("Course", course.course) for course in context.program.courses]
	context.has_access = utils.allowed_program_access(program)
	context.progress = get_course_progress(context.courses, context.program)


def get_program(program_name):
	try:
		return vmraid.get_doc("Program", program_name)
	except vmraid.DoesNotExistError:
		vmraid.throw(_("Program {0} does not exist.").format(program_name))


def get_course_progress(courses, program):
	progress = {course.name: utils.get_course_progress(course, program) for course in courses}
	return progress or {}
