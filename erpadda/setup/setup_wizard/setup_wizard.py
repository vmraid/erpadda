# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _

from .operations import company_setup
from .operations import install_fixtures as fixtures


def get_setup_stages(args=None):
	if vmraid.db.sql("select name from tabCompany"):
		stages = [
			{
				"status": _("Wrapping up"),
				"fail_msg": _("Failed to login"),
				"tasks": [{"fn": fin, "args": args, "fail_msg": _("Failed to login")}],
			}
		]
	else:
		stages = [
			{
				"status": _("Installing presets"),
				"fail_msg": _("Failed to install presets"),
				"tasks": [{"fn": stage_fixtures, "args": args, "fail_msg": _("Failed to install presets")}],
			},
			{
				"status": _("Setting up company"),
				"fail_msg": _("Failed to setup company"),
				"tasks": [{"fn": setup_company, "args": args, "fail_msg": _("Failed to setup company")}],
			},
			{
				"status": _("Setting defaults"),
				"fail_msg": "Failed to set defaults",
				"tasks": [
					{"fn": setup_defaults, "args": args, "fail_msg": _("Failed to setup defaults")},
					{"fn": stage_four, "args": args, "fail_msg": _("Failed to create website")},
					{"fn": set_active_domains, "args": args, "fail_msg": _("Failed to add Domain")},
				],
			},
			{
				"status": _("Wrapping up"),
				"fail_msg": _("Failed to login"),
				"tasks": [{"fn": fin, "args": args, "fail_msg": _("Failed to login")}],
			},
		]

	return stages


def stage_fixtures(args):
	fixtures.install(args.get("country"))


def setup_company(args):
	fixtures.install_company(args)


def setup_defaults(args):
	fixtures.install_defaults(vmraid._dict(args))


def stage_four(args):
	company_setup.create_website(args)
	company_setup.create_email_digest()
	company_setup.create_logo(args)


def fin(args):
	vmraid.local.message_log = []
	login_as_first_user(args)


def login_as_first_user(args):
	if args.get("email") and hasattr(vmraid.local, "login_manager"):
		vmraid.local.login_manager.login_as(args.get("email"))


# Only for programmatical use
def setup_complete(args=None):
	stage_fixtures(args)
	setup_company(args)
	setup_defaults(args)
	stage_four(args)
	fin(args)


def set_active_domains(args):
	domain_settings = vmraid.get_single("Domain Settings")
	domain_settings.set_active_domains(args.get("domains"))
