// Copyright (c) 2023, Ganu Reddy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Wise Sales Order"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_default("company"),
			"width": "80",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd": 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80",
			"reqd": 1,
		},
		{
			"fieldname":"parent_customer_group",
			"label": __("Parent Customer Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options("Customer Group", txt,{
					is_group:1
				});
			},
			"width": "80",
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"get_data": function(txt) {
				let base_value = frappe.query_report.get_filter_value("parent_customer_group")
				return frappe.db.get_link_options("Customer Group", txt,{
					parent_customer_group:base_value[0]
				});
			},
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"get_data": function(txt) {
				let base_value = frappe.query_report.get_filter_value("customer_group")
				return frappe.db.get_link_options("Customer", txt,{
					customer_group:base_value[0]
				});
			},
		},
		
	
		{
			"fieldname":"parent_item_group",
			"label": __("Parent Item Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			get_data: function(txt) {
				return frappe.db.get_link_options("Item Group", txt,{
					is_group:1
				});
			},
			"width": "80",
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"get_data": function(txt) {
				let base_value = frappe.query_report.get_filter_value("parent_item_group")
				return frappe.db.get_link_options("Item Group", txt,{
					parent_item_group:base_value[0]
				});
			},
		},
		
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Item",
			"get_data": function(txt) {
				let base_value = frappe.query_report.get_filter_value("item_group")
				return frappe.db.get_link_options("Item", txt,{
					item_group:base_value[0]
				});
			},
		},
		
		// {
		// 	"fieldname": "group_by_so",
		// 	"label": __("Group by Sales Order"),
		// 	"fieldtype": "Check",
		// 	"default": 0
		// }

	]
};
