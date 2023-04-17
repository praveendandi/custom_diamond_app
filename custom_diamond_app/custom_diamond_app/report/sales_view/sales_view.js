// Copyright (c) 2023, kiran and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales View"] = {
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
            // 'default':"",
            // get_data:function(txt){
            //     return new Promise((resolve,reject)=>{
            //         console.log("//////////////")
            //         frappe.call({
            //             method: "frappe.client.get_list",
            //             args: {
            //                 doctype: "Customer Group",
            //                 fields:['*'],
            //                 filters: {
            //                     parent_customer_group : ['=', frappe.db.get_link_options('Customer Group', txt,{
            //                         is_group :0
            //                     })],
            //                 },
            //             },
            //             callback: function(r, rt) {
            //                 console.log('----------',r.message.length)
            //                 if( r.message.length) {
            //                     let arra= []
            //                     r.message.forEach((res)=>{
            //                         let data =frappe.db.get_link_options("Customer Group",txt,{
            //                             parent_customer_group: res.customer_group_name
            //                         })
            //                         console.log(".........",data)
            //                         data.then((ev)=>{
            //                             ev.forEach(element => {
            //                                 console.log(element)
            //                                 arra.push(element)
            //                             });
                                        
            //                         })
            //                         console.log(data,"!!!!!!!!!!!!!")
            //                     })
            //                     setTimeout(() => {
            //                         resolve(arra)
            //                     }, 3000);
            //                 }else{
            //                     console.log("***********************",frappe.query_report.get_filter_value("customer_parent_group")[0])
            //                     let data =frappe.db.get_list('Customer Group', { 
            //                         filters: {
            //                             parent_customer_group: frappe.query_report.get_filter_value("customer_parent_group")[0], 
            //                     },
            //                     fields: ["name as label","parent_customer_group as description"], limit: 500,});
            //                     console.log(data,"dddddddddddd",data.length)
            //                     resolve(data)
            //                 }
            //             }
            //         });
            //     })
            // },

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


// erpnext.utils.add_dimensions('Sales View', 15)


// $(document).ready(function() {
//     console.log('fggggggggggggg')
    
//     setTimeout(() => {
//         let customer_parent_group = document.querySelectorAll('[data-fieldname="customer_group"]')[1]
//         console.log(customer_parent_group,"mmmmmmmmmmmmmmmmmmmmm")
//         customer_parent_group.addEventListener('click', function(event){
     
//         let isSelectAllExist = document.getElementById('customCheckBox')
//         if(isSelectAllExist){
//             isSelectAllExist.remove()
//         }
//         let myDiv = document.createElement('div');
//             myDiv.setAttribute('id','customCheckBox')
//             var checkbox = document.createElement('input');
//             checkbox.type = "checkbox";
//             checkbox.name = "name";
//             checkbox.id = "SelectAllParty";
//             var label = document.createElement('label');
//             label.htmlFor = "id";
//             label.appendChild(document.createTextNode('Select All'));
//             myDiv.appendChild(checkbox);
//             myDiv.appendChild(label);
    
//             const list = document.querySelectorAll(".multiselect-list .dropdown-menu")[1];
//             list.insertBefore(myDiv, list.children[0]);
    
//             var SelectAllParty = document.getElementById("SelectAllParty");
//             SelectAllParty.addEventListener('click', (event)=>{
//                 const totalLsit = document.querySelectorAll('[data-fieldname="customer_group"].multiselect-list .dropdown-menu .selectable-item');
//                 // let totalLsit = templist.getElementsByClassName('selectable-item ')
//                 totalLsit.forEach(element => {
//                     console.log(element)
//                     if(SelectAllParty.checked){
//                         if(!element.classList.contains('selected')){
//                             element.click()
//                         }
//                     }else{
//                         document.getElementsByClassName('multiselect-list')[0].click()
//                         element.click()
//                     }					
//                 });
//             });
        
//     })
//     }, 500);
    
//   });