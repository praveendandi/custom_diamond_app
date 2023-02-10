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
			'fieldname':"party_group",
			"label":__("Party Group"),
			"fieldtype":'Link',
			'options':'Customer Group',
			'default':"",
		},
		{
			'fieldname':'party',
			'label':__("Party"),
			'fieldtype':'MultiSelectList',
			'default':"",
			get_data:function(txt){
				return new Promise((resolve,reject)=>{
				
					 frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Customer Group",
							fields:['*'],
							filters: {
								parent_customer_group: ["=", frappe.query_report.get_filter_value("party_group")],
							},
						},
						callback: function(r, rt) {
							if( r.message.length) {
								let arra= []
								r.message.forEach((res)=>{
									let data =frappe.db.get_link_options("Customer",txt,{
										customer_group: res.customer_group_name
									})
									data.then((ev)=>{
										ev.forEach(element => {
											arra.push(element)
										});
										
									})
								})
								setTimeout(() => {
									resolve(arra)
								}, 3000);
							}else{
								let data =frappe.db.get_list('Customer', { 
									filters: {
										 customer_group: frappe.query_report.get_filter_value("party_group"), 
								},
								fields: ["name as label","name as value","customer_name as description" ], limit: 500, });
								resolve(data)
							}
						}
					});
				})
			},
		},
		{
			'fieldname':"item_category",
			"label":__("Item Category"),
			"fieldtype":'Select',
			'options':["LED","SWITCH","WIRE"],
			'default':" ",
		},

	]
};
