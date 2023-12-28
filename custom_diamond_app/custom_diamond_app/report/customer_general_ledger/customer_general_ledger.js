// Copyright (c) 2022, kiran and contributors
// For license information, please see license.txt
/* eslint-disable */


let select_all_data = function(){
	console.log("hello")
}

frappe.query_reports["Customer General Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		// {
		// 	"fieldname":"finance_book",
		// 	"label": __("Finance Book"),
		// 	"fieldtype": "Link",
		// 	"options": "Finance Book"
		// },
		{
			"fieldname":"address",
			"label": __("Address"),
			"fieldtype": "MultiSelectList",
			"reqd": 1,
			get_data:function(txt) {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Address",
						fields:['address_line1','address_line2','city','gst_state','pincode'],
						filters: {
							name: ["=", frappe.query_report.get_filter_value("company")],
						},
					},
					callback:function(r, rt) {
						let address_line1 = ''
						let address_line2 = ''
						let city = ''
						let gst_state = ''
						let pincode	 = ''
						r.message.forEach((res)=>{
							address_line1 = res.address_line1
							address_line2= res.address_line2
							city=res.city
							gst_state = res.gst_state
							pincode =res.pincode

						})
						result = `${address_line1}\n${address_line2}\n${city}\n${gst_state}\n${pincode}`
						frappe.query_report.set_filter_value('address', result)
					}
				})
				
				
            },
			
		},
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
		// {
		// 	"fieldname":"account",
		// 	"label": __("Account"),
		// 	"fieldtype": "MultiSelectList",
		// 	"options": "Account",
		// 	get_data: function(txt) {
		// 		return frappe.db.get_link_options('Account', txt, {
		// 			company: frappe.query_report.get_filter_value("company")
		// 		});
		// 	}
		// },
		// {
		// 	"fieldname":"voucher_no",
		// 	"label": __("Voucher No"),
		// 	"fieldtype": "Data",
		// 	on_change: function() {
		// 		frappe.query_report.set_filter_value('group_by', "Group by Voucher (Consolidated)");
		// 	}
		// },
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "Customer",
			"read_only":1,
		},
		{
			'fieldname':"party_group",
			"label":__("Party Group"),
			"fieldtype":'Link',
			'options':'Customer Group',
			'default':"",
			get_data:function(){
				
				console.log(data)
			}
		},
		// {
		// 	'fieldname':'sub_party',
		// 	'label':__("Sub Party"),
		// 	'fieldtype':'MultiSelectList',
		// 	'default':"",
		// 	get_data:function(txt){
		// 		return frappe.db.get_link_options("Customer Group",txt,{
		// 			parent_customer_group: frappe.query_report.get_filter_value("party_group")
		// 		})
		// 	}
		// },
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
							console.log('----------',r.message.length)
							if( r.message.length) {
								let arra= []
								r.message.forEach((res)=>{
									let data =frappe.db.get_link_options("Customer",txt,{
										customer_group: res.customer_group_name
									})
									data.then((ev)=>{
										ev.forEach(element => {
											console.log(element)
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
			on_change: function() {
				var party_type = frappe.query_report.get_filter_value('party_type');
				var parties = frappe.query_report.get_filter_value('party');

				if(!party_type || parties.length === 0 || parties.length > 1) {
					frappe.query_report.set_filter_value('party_name', "");
					frappe.query_report.set_filter_value('tax_id', "");
					return;
				} else {
					var party = parties[0];
					var fieldname = erpnext.utils.get_party_name(party_type) || "name";
					frappe.db.get_value(party_type, party, fieldname, function(value) {
						frappe.query_report.set_filter_value('party_name', value[fieldname]);
					});

					if (party_type === "Customer" || party_type === "Supplier") {
						frappe.db.get_value(party_type, party, "tax_id", function(value) {
							frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
						});
					}
				}
			}
		},
		{
			"fieldname":"party_name",
			"label": __("Party Name"),
			"fieldtype": "Data",
			"hidden": 0
		},
		{
			"fieldname":"group_by",
			"label": __("Group by"),
			"fieldtype": "Select",
			"options": [
				"",
				{
					label: __("Group by Voucher"),
					value: "Group by Voucher",
				},
				{
					label: __("Group by Voucher (Consolidated)"),
					value: "Group by Voucher (Consolidated)",
				},
				{
					label: __("Group by Account"),
					value: "Group by Account",
				},
				{
					label: __("Group by Party"),
					value: "Group by Party",
				},
			],
			"default": "Group by Voucher (Consolidated)"
		},
		// {
		// 	"fieldname":"tax_id",
		// 	"label": __("Tax Id"),
		// 	"fieldtype": "Data",
		// 	"hidden": 1
		// },
		// {
		// 	"fieldname": "presentation_currency",
		// 	"label": __("Currency"),
		// 	"fieldtype": "Select",
		// 	"options": erpnext.get_presentation_currency_list()
		// },
		// {
		// 	"fieldname":"cost_center",
		// 	"label": __("Cost Center"),
		// 	"fieldtype": "MultiSelectList",
		// 	get_data: function(txt) {
		// 		return frappe.db.get_link_options('Cost Center', txt, {
		// 			company: frappe.query_report.get_filter_value("company")
		// 		});
		// 	}
		// },
		// {
		// 	"fieldname":"project",
		// 	"label": __("Project"),
		// 	"fieldtype": "MultiSelectList",
		// 	get_data: function(txt) {
		// 		return frappe.db.get_link_options('Project', txt, {
		// 			company: frappe.query_report.get_filter_value("company")
		// 		});
		// 	}
		// },
		{
			"fieldname": "include_dimensions",
			"label": __("Consider Accounting Dimensions"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "show_opening_entries",
			"label": __("Show Opening Entries"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "show_cancelled_entries",
			"label": __("Show Cancelled Entries"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "show_net_values_in_party_account",
			"label": __("Show Net Values in Party Account"),
			"fieldtype": "Check"
		}
	]
}



erpnext.utils.add_dimensions('Customer General Ledger', 15)


$(document).ready(function() {
	console.log('fggggggggggggg')
	
	setTimeout(() => {
		let party_group = document.querySelectorAll('input[data-fieldname="party_group"]')[0]
	party_group.addEventListener('click', function(event){
	 
		let isSelectAllExist = document.getElementById('customCheckBox')
		if(isSelectAllExist){
			isSelectAllExist.remove()
		}
		let myDiv = document.createElement('div');
			myDiv.setAttribute('id','customCheckBox')
			var checkbox = document.createElement('input');
			checkbox.type = "checkbox";
			checkbox.name = "name";
			checkbox.id = "SelectAllParty";
			var label = document.createElement('label');
			label.htmlFor = "id";
			label.appendChild(document.createTextNode('Select All'));
			myDiv.appendChild(checkbox);
			myDiv.appendChild(label);
	
			const list = document.querySelectorAll(".multiselect-list .dropdown-menu")[0];
			list.insertBefore(myDiv, list.children[0]);
	
			var SelectAllParty = document.getElementById("SelectAllParty");
			SelectAllParty.addEventListener('click', (event)=>{
				let totalLsit = document.getElementsByClassName('selectable-item ')
				totalLsit.forEach(element => {
					console.log(SelectAllParty.checked)
					if(SelectAllParty.checked){
						if(!element.classList.contains('selected')){
							element.click()
						}
					}else{
						document.getElementsByClassName('multiselect-list')[0].click()
						element.click()
					}					
				});
			});
		
	})
	}, 500);
	
  });