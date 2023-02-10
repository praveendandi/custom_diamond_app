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
  
  
def get_conditions(filters):
    condition = ""
    condition += f"posting_date Between'{filters.from_date}' and '{filters.to_date}'"
    if filters.party_group:
        customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters.party_group},["name"])
        if len(customer_group)>0:
            total_group = tuple([i["name"] for i in customer_group])
            condition += f" and customer_group IN {total_group}"
    return condition

def get_data(filters,result_condtions):
    data = frappe.db.sql("""select customer,customer_name,customer_group,sum(grand_total) as grand_total
                      from `tabSales Invoice` Where docstatus = 1  and is_return != 1 and {conditions} Group by customer """.format(conditions=result_condtions),as_dict =1)
    print(data,"//////////////////////")
    for i in data:
        data_return = frappe.db.sql("""select customer,customer_name,customer_group,sum(grand_total) as return_amount
                        from `tabSales Invoice` Where docstatus = 1  and is_return = 1 and customer = '{conditions}' Group by customer """.format(conditions=i["customer"]),as_dict =1)
        if len(data_return)>0:
            i["return_amount"] = data_return[0]["return_amount"]
            i["total_amount"] = i['grand_total'] + data_return[0]['return_amount']
    
    print(data,"//////////////////////")
    # print("""select customer,customer_name,customer_group,sum(grand_total) as grand_total
    #                   from `tabSales Invoice` Where {conditions} Group by customer """.format(conditions=result_condtions),"//////////")
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
            "label": _("Party Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": _("Total Bills Amount"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 250,
        },
        {
            "label": _("Total Returns Amount"),
            "fieldname": "return_amount",
            "fieldtype": "Currency",
            "width": 250,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 250,
        }
    ]
    return columns