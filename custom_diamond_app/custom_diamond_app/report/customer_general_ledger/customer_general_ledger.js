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
			// 'onchange':function(){
			// 	console.log("hello")
			// }
			// 'default':,
			
			// get_data:function(){
			// 	data = frappe.db.get_list('party_type','party_group',fields=['customer_name'])
			// 	console.log(data)
			// }
		},
		{
			'fieldname':'party',
			'label':__("Party"),
			'fieldtype':'MultiSelectList',
			'default':"",
			get_data:function(txt){
				return frappe.db.get_link_options("Customer",txt,{
					customer_group: frappe.query_report.get_filter_value("party_group")
				})
			},
		},
		{
			"fieldname":"party_name",
			"label": __("Party Name"),
			"fieldtype": "Data",
			"hidden": 1
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