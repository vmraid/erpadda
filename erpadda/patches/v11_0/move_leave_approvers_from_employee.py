import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("hr", "doctype", "department_approver")
	vmraid.reload_doc("hr", "doctype", "employee")
	vmraid.reload_doc("hr", "doctype", "department")

	if vmraid.db.has_column("Department", "leave_approver"):
		rename_field("Department", "leave_approver", "leave_approvers")

	if vmraid.db.has_column("Department", "expense_approver"):
		rename_field("Department", "expense_approver", "expense_approvers")

	if not vmraid.db.table_exists("Employee Leave Approver"):
		return

	approvers = vmraid.db.sql(
		"""select distinct app.leave_approver, emp.department from
	`tabEmployee Leave Approver` app, `tabEmployee` emp
		where app.parenttype = 'Employee'
		and emp.name = app.parent
		""",
		as_dict=True,
	)

	for record in approvers:
		if record.department:
			department = vmraid.get_doc("Department", record.department)
			if not department:
				return
			if not len(department.leave_approvers):
				department.append("leave_approvers", {"approver": record.leave_approver}).db_insert()
