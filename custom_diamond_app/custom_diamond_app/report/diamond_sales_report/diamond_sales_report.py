# Copyright (c) 2023, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
import pandas as pd
from frappe.utils import flt

def execute(filters=None):
    print(filters,"////////////////...............")
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
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":('IN',(filters['customer_parent_group']))},["name"])
            if len(customer_group)>1:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and customer_group IN {total_group}"
            else:
                condition += f" and customer_group = '{total_group}'"
        if filters['customer_group'] and not filters['customer']:
            if len(filters['customer_group'])>1:
                customer_group = tuple([i for i in filters['customer_group']])
                print(customer_group,".................")
                condition += f" and customer_group IN {customer_group}"
            else:
                customer_group = filters["customer_group"][0]
                condition += f" and customer_group = '{customer_group}'"
        
        if filters['customer']:
            if len(filters['customer'])>1:
                customer = tuple([i for i in filters['customer']])
                print(customer,".................")
                condition += f" and customer IN {customer}"
            else:
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
            
        # if filters['item']:
        #     item = filters["item"][0]
        #     condition += f" and soi.item_code = '{item}'"
            
        if filters['customer_parent_group'] and not filters['customer_group']:
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters['customer_parent_group'][0]},["name"])
            if len(customer_group)>2:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and si.customer_group IN {total_group}"
            else:
                total_group = customer_group[0]['name']
                condition += f" and si.customer_group = '{total_group}'"
                
        if filters['customer_group']:
            customer_group = filters["customer_group"][0]
            condition += f" and si.customer_group = '{customer_group}'"
        
        if filters['customer']:
            customer = filters["customer"][0]
            condition += f" and si.customer = '{customer}'"
        return condition
    if filters.type_of_tree == "Item Group Wise":
        condition = ""
        condition += f"si.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        
        if not filters.net_salses:
            condition+=f' and si.is_return != 1'
            
        if filters['customer_parent_group'] and not filters['customer_group']:
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters['customer_parent_group'][0]},["name"])
            if len(customer_group)>2:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and si.customer_group IN {total_group}"
            else:
                total_group = customer_group[0]['name']
                condition += f" and si.customer_group = '{total_group}'"
                
        if filters['customer_group']:
            customer_group = filters["customer_group"][0]
            condition += f" and si.customer_group = '{customer_group}'"
        
        if filters['customer']:
            customer = filters["customer"][0]
            condition += f" and si.customer = '{customer}'"
            
        return condition
    if filters.type_of_tree == "Item Group Wise Qty":
        condition = ""
        condition += f"si.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if not filters.net_salses:
            condition+=f' and si.is_return != 1'
            pass
        if filters['customer_parent_group'] and not filters['customer_group']:
            customer_group = frappe.db.get_list("Customer Group",{"parent_customer_group":filters['customer_parent_group'][0]},["name"])
            if len(customer_group)>2:
                total_group = tuple([i["name"] for i in customer_group])
                condition += f" and si.customer_group IN {total_group}"
            else:
                total_group = customer_group[0]['name']
                condition += f" and si.customer_group = '{total_group}'"
                
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
        
        date = f"posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        for i in data:
            data_return = frappe.db.sql("""select customer,customer_name,customer_group,sum(grand_total) as return_amount,sum(base_net_total) as taxable_return_amount
                            from `tabSales Invoice` Where docstatus = 1  and is_return = 1 and customer = '{conditions}'  and {date} Group by customer """.format(conditions=i["customer"],date=date),as_dict =1)
            
            if len(data_return)>0:
                parent_customer_group = frappe.db.sql("""select parent_customer_group from `tabCustomer Group` where name = '{}' """.format(i.customer_group),as_dict=1)
                i['parent_customer_group'] = parent_customer_group[0]["parent_customer_group"]
                i["return_amount"] = data_return[0]["return_amount"]
                i["taxable_return_amount"] = data_return[0]["taxable_return_amount"]
                i['taxable_total_amount'] = flt(i["taxable_amount"] + data_return[0]["taxable_return_amount"])
                i["total_amount"] = flt(i['grand_total'] + data_return[0]['return_amount'])
                
            if not len(data_return)>0:
                parent_customer_group = frappe.db.sql("""select parent_customer_group from `tabCustomer Group` where name = '{}' """.format(i.customer_group),as_dict=1)
                i['parent_customer_group'] = parent_customer_group[0]["parent_customer_group"]
                i["total_amount"] = flt(i['grand_total'])
                i["taxable_total_amount"] = flt(i['taxable_amount'])
        
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
    
    if filters.type_of_tree == "Item Group Wise":
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group_wise = frappe.db.sql("""select name from `tabItem Group` where parent_item_group = '{}' """.format(parent_group),as_dict=1)
            if filters.item_group:
                name = tuple([i["name"] for i in item_group_wise if i["name"] not in filters["item_group"]])
            else:
                name = tuple([i["name"] for i in item_group_wise])
                
            data = frappe.db.sql("""select si.customer,si.customer_group,soi.item_group,SUM(soi.amount) as amount from `tabSales Invoice` as si,`tabSales Invoice Item` as soi Where soi.parent = si.name and
                                si.docstatus = 1 and soi.item_group IN {name} and {condition}
                                Group By soi.item_group ,si.customer_group , si.customer ORDER BY si.customer""".format(name=name,condition=result_condtions), as_dict=1)
            if len(data) >0:
                data_1 = []
                for i in data:
                    value = {}
                    value['customer'] = i.get('customer')
                    value['customer_group'] = i.get('customer_group')
                    value[i.get('item_group')] = i.get("amount")
                    value['total'] = i.get("amount")
                    data_1.append(value)
                    
                data_convert = pd.DataFrame.from_records(data_1,)
                final_data = data_convert.groupby(['customer',"customer_group"],as_index=False).sum()
                convert_data = final_data.to_dict('records')
                return convert_data
    
    if filters.type_of_tree == "Item Group Wise Qty":
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group_wise = frappe.db.sql("""select name from `tabItem Group` where parent_item_group = '{}' """.format(parent_group),as_dict=1)
            name = tuple([i["name"] for i in item_group_wise])
            data = frappe.db.sql("""select si.customer,si.customer_group,soi.item_group,SUM(soi.qty) as qty from `tabSales Invoice` as si,`tabSales Invoice Item` as soi Where soi.parent = si.name and
                                si.docstatus = 1 and soi.item_group IN {name} and {condition}
                                Group By soi.item_group ,si.customer_group , si.customer ORDER BY si.customer""".format(name=name,condition=result_condtions), as_dict=1)
            if len(data) >0:
                data_1 = []
               
                for i in data:
                    value = {}
                    value['customer'] = i.get('customer')
                    value['customer_group'] = i.get('customer_group')
                    value[i.get('item_group')] = i.get("qty")
                    value['total_qty'] = i.get("qty")
                    data_1.append(value)
                    
                data_convert = pd.DataFrame.from_records(data_1,)
                final_data = data_convert.groupby(['customer',"customer_group"],as_index=False).sum()
                convert_data = final_data.to_dict('records')
                return convert_data
            
    
    
def get_columns(filters):
    columns = []
    if filters.type_of_tree == 'Customer Wise' or filters.type_of_tree == 'Item Wise':
        columns += [
            {
                "label": _("Party"),
                "fieldname": "customer",
                "fieldtype": "Link",
                "options": "Customer",
                "width": 150,
            },
            {
                "label": _("Party Name"),
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Parent Customer Group"),
                "fieldname": "parent_customer_group",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Party Group"),
                "fieldname": "customer_group",
                "fieldtype": "Data",
                "width": 150,
            }
    ]
    if filters.type_of_tree == 'Customer Wise':
        columns +=[
        {
            "label": _("Taxable Amount"),
            "fieldname": "taxable_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Taxable Return Amount"),
            "fieldname": "taxable_return_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Net Sale"),
            "fieldname": "taxable_total_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Total Bills Amount"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Total Returns Amount"),
            "fieldname": "return_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Net Sale After GST"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150,
        }
        ]

    if filters.type_of_tree == 'Item Wise':
        columns += [
            {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
       {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "options": "Item Group",
            "width": 150,
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150,
        },
        {
            "label": _("Item Parent Group"),
            "fieldname": "parent_item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150,
        },
        {
            "label": _("amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        ]
    if filters.type_of_tree == 'Item Group Wise' and filters['item_parent_Group']:
        columns +=[
        {
            "label": _("Party"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Party Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150,
        },
        ]
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group = frappe.db.get_list("Item Group",{"parent_item_group":parent_group},pluck='name')
        if filters['item_group']:
            columns += [{"label": _(each),"fieldname": each, "fieldtype": "Currency", "width": 150} for each in item_group if each not in filters['item_group']]
        else:
            columns += [{"label": _(each),"fieldname": each, "fieldtype": "Currency", "width": 150} for each in item_group]
 
        columns +=[{"label":_("Total"),"fieldname":"total","fieldtype":"Currency","width":150}]
        
    if filters.type_of_tree == 'Item Group Wise Qty' and filters['item_parent_Group']:
        columns +=[
        {
            "label": _("Party"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Party Group"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150,
        },
        ]
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group = frappe.db.get_list("Item Group",{"parent_item_group":parent_group},pluck='name')
        columns += [{"label": _(each),"fieldname": each, "fieldtype": "Data", "width": 150} for each in item_group]
        columns +=[{"label":_("Total Qty"),"fieldname":"total_qty","fieldtype":"Data","width":150}]

    
    return columns