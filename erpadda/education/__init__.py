import vmraid
from vmraid import _


class StudentNotInGroupError(vmraid.ValidationError):
	pass


def validate_student_belongs_to_group(student, student_group):
	groups = vmraid.db.get_all("Student Group Student", ["parent"], dict(student=student, active=1))
	if not student_group in [d.parent for d in groups]:
		vmraid.throw(
			_("Student {0} does not belong to group {1}").format(
				vmraid.bold(student), vmraid.bold(student_group)
			),
			StudentNotInGroupError,
		)
