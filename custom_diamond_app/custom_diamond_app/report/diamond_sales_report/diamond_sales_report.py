# Copyright (c) 2023, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict

def execute(filters=None):
    if not filters:
        return [], []

    validate_filters(filters)
    result_columns = get_columns(filters)
    result_condtions = get_conditions(filters)
    result_data = get_data(filters,result_condtions)
 
    return result_columns, result_data


def validate_filters(filters):
    if not filters.get("from_date") and not filters.get("to_date"):
        frappe.throw(
            _("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date")))
        )
               
    if filters.get("from_date") > filters.get("to_date"):
        frappe.throw(
            _("{0} not greater than To Date").format(frappe.bold(_("From Date")))
        )

  
def get_conditions(filters):
    if filters.type_of_tree == "Customer Wise": 
        condition = ""
        condition += f"posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if filters['customer_parent_group'] and not filters['customer_group']:
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters['customer_parent_group'][0]},["name"])
            if len(customer_group)>0:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and customer_group IN {total_group}"
        if filters['customer_group']:
            customer_group = filters["customer_group"][0]
            condition += f" and customer_group = '{customer_group}'"
        
        if filters['customer']:
            customer = filters["customer"][0]
            condition += f" and customer = '{customer}'"
            
        return condition
    
    if filters.type_of_tree == "Item Wise":
        condition = ""
        condition += f"si.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if filters["item_parent_Group"] and not filters['item_group']:
            items_groups = frappe.db.get_list("Item Group",{"parent_item_group":filters["item_parent_Group"][0]},["name"])
            if len(items_groups)>0:
                total_group = tuple([i["name"] for i in items_groups])
                condition += f" and soi.item_group IN {total_group}"
                
        if filters['item_group']:
            item_group = filters["item_group"][0]
            condition += f" and soi.item_group = '{item_group}'"
            
        if filters['item']:
            item = filters["item"][0]
            condition += f" and soi.item_code = '{item}'"
            
        if filters['customer_parent_group'] and not filters['customer_group']:
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters['customer_parent_group'][0]},["name"])
            if len(customer_group)>0:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and si.customer_group IN {total_group}"
                
        if filters['customer_group']:
            customer_group = filters["customer_group"][0]
            condition += f" and si.customer_group = '{customer_group}'"
        
        if filters['customer']:
            customer = filters["customer"][0]
            condition += f" and si.customer = '{customer}'"
        return condition

def get_data(filters,result_condtions):
    if filters.type_of_tree == "Customer Wise":
        data = frappe.db.sql("""select customer,customer_name,customer_group,sum(grand_total) as grand_total,sum(base_net_total) as taxable_amount
                        from `tabSales Invoice` Where docstatus = 1  and is_return != 1 and {conditions} Group by customer """.format(conditions=result_condtions),as_dict =1)
        for i in data:
            data_return = frappe.db.sql("""select customer,customer_name,customer_group,sum(grand_total) as return_amount,sum(base_net_total) as taxable_return_amount
                            from `tabSales Invoice` Where docstatus = 1  and is_return = 1 and customer = '{conditions}' Group by customer """.format(conditions=i["customer"]),as_dict =1)
            
            if len(data_return)>0:
                parent_customer_group = frappe.db.sql("""select parent_customer_group from `tabCustomer Group` where name = '{}' """.format(i.customer_group),as_dict=1)
                i['parent_customer_group'] = parent_customer_group[0]["parent_customer_group"]
                i["return_amount"] = data_return[0]["return_amount"]
                i["taxable_return_amount"] = data_return[0]["taxable_return_amount"]
                i["total_amount"] = i['grand_total'] + data_return[0]['return_amount']
                
            if not len(data_return)>0:
                parent_customer_group = frappe.db.sql("""select parent_customer_group from `tabCustomer Group` where name = '{}' """.format(i.customer_group),as_dict=1)
                i['parent_customer_group'] = parent_customer_group[0]["parent_customer_group"]
                i["total_amount"] = i['grand_total']
        
        # print(data,"//////////////////////")
        # print("""select customer,customer_name,customer_group,sum(grand_total) as grand_total
        #                   from `tabSales Invoice` Where {conditions} Group by customer """.format(conditions=result_condtions),"//////////")
        return data
    if filters.type_of_tree == "Item Wise":
        
        data = frappe.db.sql("""select si.customer,si.customer_group,si.customer_name,soi.item_code,soi.item_group,soi.item_name,SUM(amount) as amount
                             FROM
                             `tabSales Invoice` as si,
                             `tabSales Invoice Item` as soi
                             WHERE
                             soi.parent = si.name and
                             si.docstatus = 1  and si.is_return != 1 and {conditions}
                             GROUP BY
                             si.customer,soi.item_code
                             """.format(conditions=result_condtions),as_dict=1)

        if len(data)>0:
            for i in data:
                parent_item_group = frappe.db.sql("""select parent_item_group from `tabItem Group` where name = '{}' """.format(i.item_group),as_dict=1)
                parent_customer_group = frappe.db.sql("""select parent_customer_group from `tabCustomer Group` where name = '{}' """.format(i.customer_group),as_dict=1)
                i['parent_customer_group'] = parent_customer_group[0]["parent_customer_group"]
                i['parent_item_group'] = parent_item_group[0]['parent_item_group']
                
        return data
def get_columns(filters):
    
    columns = [
        {
            "label": _("Party"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 250,
        },
        {
            "label": _("Party Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": _("Parent Customer Group"),
            "fieldname": "parent_customer_group",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": _("Party Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 250,
        }
    ]
    if filters.type_of_tree == 'Customer Wise':
        columns +=[
        {
            "label": _("Taxable Amount"),
            "fieldname": "taxable_amount",
            "fieldtype": "Currency",
            "width": 250,
        },
        {
            "label": _("Taxable Return Amount"),
            "fieldname": "taxable_return_amount",
            "fieldtype": "Currency",
            "width": 250,
        },
        {
            "label": _("Total Bills Amount"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 200,
        },
        {
            "label": _("Total Returns Amount"),
            "fieldname": "return_amount",
            "fieldtype": "Currency",
            "width": 200,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 200,
        }
        ]

    if filters.type_of_tree == 'Item Wise':
        columns += [
            {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
       {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "options": "Item Group",
            "width": 250,
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 250,
        },
        {
            "label": _("Item Parent Group"),
            "fieldname": "parent_item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 250,
        },
        {
            "label": _("amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 250,
        },
        ]
    
    return columns