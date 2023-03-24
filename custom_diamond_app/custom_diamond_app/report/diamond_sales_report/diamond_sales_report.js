// Copyright (c) 2023, kiran and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Diamond Sales Report"] = {
	"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			'fieldname':"type_of_tree",
			"label": __("Type Of Tree"),
			"fieldtype": "Select",
			"options":["Customer Wise","Item Wise","Item Group Wise","Item Group Wise Qty"],
			"default":"Customer Wise"
		},
		{
			'fieldname':"customer_parent_group",
			"label":__("Customer Parent Group"),
			"fieldtype":'MultiSelectList',
			'default':"",
			get_data:function(txt) {
				return frappe.db.get_link_options('Customer Group', txt,{
					is_group :1
				});
			}
		},
		{
			'fieldname':"customer_group",
			"label":__("Customer Group"),
			"fieldtype":'MultiSelectList',
			'default':"",
			get_data:function(txt) {	
				let base_value = frappe.query_report.get_filter_value('customer_parent_group')
				return frappe.db.get_link_options('Customer Group', txt,{
					parent_customer_group :base_value[0]
				});
			}
		},
		{
			'fieldname':'customer',
			'label':__("Customer"),
			'fieldtype':'MultiSelectList',
			'default':"",
			get_data:function(txt) {	
				let base_value = frappe.query_report.get_filter_value('customer_group')
				return frappe.db.get_link_options('Customer', txt,{
					customer_group :base_value[0]
				});
			}
		},
		{
			"fieldname":"item_parent_Group",
			"label":__("Item Parent Group"),
			"fieldtype":"MultiSelectList",
			"depends_on": doc.type_of_tree=='Item Group Wise',
			get_data:function(txt) {	
				return frappe.db.get_link_options('Item Group', txt,{
					is_group :1
				});
			}
		},
		{
			"fieldname":"item_group",
			"label":__("Item Group"),
			"fieldtype":"MultiSelectList",
			get_data:function(txt) {	
				let base_value = frappe.query_report.get_filter_value('item_parent_Group')
				return frappe.db.get_link_options('Item Group', txt,{
					parent_item_group :base_value[0]
				});
			}
		},
		{
			"fieldname":"item",
			"label":__("Item"),
			"fieldtype":"MultiSelectList",
			get_data:function(txt) {	
				let base_value = frappe.query_report.get_filter_value('item_group')
				return frappe.db.get_link_options('Item', txt,{
					item_group :base_value[0]
				});
			}
		},
		{
			'fieldname':"net_salses",
			"label":__("Net Salses"),
			"fieldtype":'Check',
			'default':0,
		},
	]
};
