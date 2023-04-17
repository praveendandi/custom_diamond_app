// Copyright (c) 2023, kiran and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Reorder Level Report"] = {
	"filters": [
		{
			'fieldname':"type_of_tree",
			"label": __("Type Of Tree"),
			"fieldtype": "Select",
			"options":["Item Wise"],
			"default":"Item Wise"
		},
		// {
		// 	'fieldname':"warehouse",
		// 	"label": __("WareHouse"),
		// 	"fieldtype": "Link",
		// 	"options":'Warehouse',
		// },

	]
};
