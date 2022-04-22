import vmraid

from erpadda.setup.install import create_default_success_action


def execute():
	vmraid.reload_doc("core", "doctype", "success_action")
	create_default_success_action()
