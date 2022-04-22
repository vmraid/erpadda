# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class DepartmentApprover(Document):
	pass


@vmraid.whitelist()
@vmraid.validate_and_sanitize_search_inputs
def get_approvers(doctype, txt, searchfield, start, page_len, filters):

	if not filters.get("employee"):
		vmraid.throw(_("Please select Employee first."))

	approvers = []
	department_details = {}
	department_list = []
	employee = vmraid.get_value(
		"Employee",
		filters.get("employee"),
		["employee_name", "department", "leave_approver", "expense_approver", "shift_request_approver"],
		as_dict=True,
	)

	employee_department = filters.get("department") or employee.department
	if employee_department:
		department_details = vmraid.db.get_value(
			"Department", {"name": employee_department}, ["lft", "rgt"], as_dict=True
		)
	if department_details:
		department_list = vmraid.db.sql(
			"""select name from `tabDepartment` where lft <= %s
			and rgt >= %s
			and disabled=0
			order by lft desc""",
			(department_details.lft, department_details.rgt),
			as_list=True,
		)

	if filters.get("doctype") == "Leave Application" and employee.leave_approver:
		approvers.append(
			vmraid.db.get_value("User", employee.leave_approver, ["name", "first_name", "last_name"])
		)

	if filters.get("doctype") == "Expense Claim" and employee.expense_approver:
		approvers.append(
			vmraid.db.get_value("User", employee.expense_approver, ["name", "first_name", "last_name"])
		)

	if filters.get("doctype") == "Shift Request" and employee.shift_request_approver:
		approvers.append(
			vmraid.db.get_value(
				"User", employee.shift_request_approver, ["name", "first_name", "last_name"]
			)
		)

	if filters.get("doctype") == "Leave Application":
		parentfield = "leave_approvers"
		field_name = "Leave Approver"
	elif filters.get("doctype") == "Expense Claim":
		parentfield = "expense_approvers"
		field_name = "Expense Approver"
	elif filters.get("doctype") == "Shift Request":
		parentfield = "shift_request_approver"
		field_name = "Shift Request Approver"
	if department_list:
		for d in department_list:
			approvers += vmraid.db.sql(
				"""select user.name, user.first_name, user.last_name from
				tabUser user, `tabDepartment Approver` approver where
				approver.parent = %s
				and user.name like %s
				and approver.parentfield = %s
				and approver.approver=user.name""",
				(d, "%" + txt + "%", parentfield),
				as_list=True,
			)

	if len(approvers) == 0:
		error_msg = _("Please set {0} for the Employee: {1}").format(
			field_name, vmraid.bold(employee.employee_name)
		)
		if department_list:
			error_msg += " " + _("or for Department: {0}").format(vmraid.bold(employee_department))
		vmraid.throw(error_msg, title=_(field_name + " Missing"))

	return set(tuple(approver) for approver in approvers)
