# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import vmraid
from vmraid.model.document import Document


class WebsiteOffer(Document):
	pass


@vmraid.whitelist(allow_guest=True)
def get_offer_details(offer_id):
	return vmraid.db.get_value("Website Offer", {"name": offer_id}, ["offer_details"])
