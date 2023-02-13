// Copyright (c) 2023, Ganu Reddy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item wise Sales Order Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Customer",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Customer", txt);
			},
			// "reqd": 1,
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Customer Group",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Customer Group", txt);
			},
			// "reqd": 1,
		},
		// {
		// 	"fieldname": "sales_order",
		// 	"label": __("Sales Order"),
		// 	"fieldtype": "MultiSelectList",
		// 	"width": "80",
		// 	"options": "Sales Order",
		// 	"get_data": function(txt) {
		// 		return frappe.db.get_link_options("Sales Order", txt);
		// 	},
		// 	"get_query": () =>{
		// 		return {
		// 			filters: { "docstatus": 1 }
		// 		}
		// 	}
		// },
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			get_data: function(txt) {
				let status = ["To Bill", "To Deliver", "To Deliver and Bill", "Completed"]
				let options = []
				for (let option of status){
					options.push({
						"value": option,
						"label": __(option),
						"description": ""
					})
				}
				return options
			}
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Item Group",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Item Group", txt);
			},
			// "reqd": 1,
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Item", txt);
			},
			
			// "reqd": 1,
		},
		
		// {
		// 	"fieldname": "group_by_so",
		// 	"label": __("Group by Sales Order"),
		// 	"fieldtype": "Check",
		// 	"default": 0
		// }

	]
};
