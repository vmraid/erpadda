# Copyright (c) 2021, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid


def execute():

	job_card = vmraid.qb.DocType("Job Card")
	(
		vmraid.qb.update(job_card)
		.set(job_card.status, "Completed")
		.where(
			(job_card.docstatus == 1)
			& (job_card.for_quantity <= job_card.total_completed_qty)
			& (job_card.status.isin(["Work In Progress", "Material Transferred"]))
		)
	).run()
