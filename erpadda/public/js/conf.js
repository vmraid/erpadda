// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.provide('erpadda');

// preferred modules for breadcrumbs
$.extend(vmraid.breadcrumbs.preferred, {
	"Item Group": "Stock",
	"Customer Group": "Selling",
	"Supplier Group": "Buying",
	"Territory": "Selling",
	"Sales Person": "Selling",
	"Sales Partner": "Selling",
	"Brand": "Stock",
	"Maintenance Schedule": "Support",
	"Maintenance Visit": "Support"
});

$.extend(vmraid.breadcrumbs.module_map, {
	'ERPAdda Integrations': 'Integrations',
	'Geo': 'Settings',
	'Portal': 'Website',
	'Utilities': 'Settings',
	'E-commerce': 'Website',
	'Contacts': 'CRM'
});
