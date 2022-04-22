# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

test_dependencies = ["Employee"]

import vmraid

test_records = vmraid.get_test_records("Sales Person")

test_ignore = ["Item Group"]
