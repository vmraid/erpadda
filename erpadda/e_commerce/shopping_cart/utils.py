# Copyright (c) 2021, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt
import vmraid

from erpadda.e_commerce.doctype.e_commerce_settings.e_commerce_settings import is_cart_enabled


def show_cart_count():
	if (
		is_cart_enabled()
		and vmraid.db.get_value("User", vmraid.session.user, "user_type") == "Website User"
	):
		return True

	return False


def set_cart_count(login_manager):
	# since this is run only on hooks login event
	# make sure user is already a customer
	# before trying to set cart count
	user_is_customer = is_customer()
	if not user_is_customer:
		return

	if show_cart_count():
		from erpadda.e_commerce.shopping_cart.cart import set_cart_count

		# set_cart_count will try to fetch existing cart quotation
		# or create one if non existent (and create a customer too)
		# cart count is calculated from this quotation's items
		set_cart_count()


def clear_cart_count(login_manager):
	if show_cart_count():
		vmraid.local.cookie_manager.delete_cookie("cart_count")


def update_website_context(context):
	cart_enabled = is_cart_enabled()
	context["shopping_cart_enabled"] = cart_enabled


def is_customer():
	if vmraid.session.user and vmraid.session.user != "Guest":
		contact_name = vmraid.get_value("Contact", {"email_id": vmraid.session.user})
		if contact_name:
			contact = vmraid.get_doc("Contact", contact_name)
			for link in contact.links:
				if link.link_doctype == "Customer":
					return True

		return False
