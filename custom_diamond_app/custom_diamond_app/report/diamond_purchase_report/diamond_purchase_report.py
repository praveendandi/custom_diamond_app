# Copyright (c) 2023, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
import pandas as pd
from frappe.utils import flt

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
    if filters.type_of_tree == "Supplier Wise": 
        condition = ""
        condition += f"posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if filters['supplier_parent_group'] and not filters['supplier_group']:
            supplier_group = frappe.db.get_list("Supplier Group",{"parent_supplier_group":filters['supplier_parent_group'][0]},["name"])
            if len(supplier_group)>0:
                total_group = tuple([i["name"] for i in supplier_group])
                condition += f" and supplier_group IN {total_group}"
        if filters['supplier_group']:
            supplier_group = filters["supplier_group"][0]
            condition += f" and supplier_group = '{supplier_group}'"
        
        if filters['supplier']:
            supplier = filters["supplier"][0]
            condition += f" and supplier = '{supplier}'"
            
        return condition
    
    if filters.type_of_tree == "Item Wise":
        condition = ""
        condition += f"pi.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if filters["item_parent_Group"] and not filters['item_group']:
            items_groups = frappe.db.get_list("Item Group",{"parent_item_group":filters["item_parent_Group"][0]},["name"])
            if len(items_groups)>0:
                total_group = tuple([i["name"] for i in items_groups])
                condition += f" and poi.item_group IN {total_group}"
                
        if filters['item_group']:
            item_group = filters["item_group"][0]
            condition += f" and poi.item_group = '{item_group}'"
            
        if filters['item']:
            item = filters["item"][0]
            condition += f" and poi.item_code = '{item}'"
            
        if filters['supplier_parent_group'] and not filters['supplier_group']:
            supplier_group = frappe.db.get_list("Supplier Group",{"parent_supplier_group":filters['supplier_parent_group'][0]},["name"])
            if len(supplier_group)>2:
                total_group = tuple([i["name"] for i in supplier_group])
                condition += f" and pi.supplier_group IN {total_group}"
            else:
                total_group = customer_group[0]['name']
                condition += f" and pi.supplier_group = '{total_group}'"
                
        if filters['supplier_group']:
            supplier_group = filters["supplier_group"][0]
            condition += f" and pi.supplier_group = '{supplier_group}'"
        
        if filters['supplier']:
            supplier = filters["supplier"][0]
            condition += f" and pi.supplier = '{supplier}'"
        return condition
    if filters.type_of_tree == "Item Group Wise":
        condition = ""
        condition += f"pi.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if not filters.net_salses:
            condition+=f' and pi.is_return != 1'
        if filters['supplier_parent_group'] and not filters['supplier_group']:
            supplier_group = frappe.db.get_list("Supplier Group",{"parent_supplier_group":filters['supplier_parent_group'][0]},["name"])
            if len(customer_group)>2:
                total_group = tuple([i["name"] for i in supplier_group])
                condition += f" and pi.supplier_group IN {total_group}"
            else:
                total_group = customer_group[0]['name']
                condition += f" and pi.supplier_group = '{total_group}'"
                
        if filters['supplier_group']:
            supplier_group = filters["supplier_group"][0]
            condition += f" and pi.supplier_group = '{supplier_group}'"
        
        if filters['supplier']:
            customer = filters["supplier"][0]
            condition += f" and pi.supplier = '{customer}'"
            
        return condition
    if filters.type_of_tree == "Item Group Wise Qty":
        condition = ""
        condition += f"pi.posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        if not filters.net_salses:
            condition+=f' and pi.is_return != 1'

        if filters['supplier_parent_group'] and not filters['supplier_group']:
            supplier_group = frappe.db.get_list("Supplier Group",{"parent_supplier_group":filters['supplier_parent_group'][0]},["name"])
            if len(supplier_group)>2:
                total_group = tuple([i["name"] for i in supplier_group])
                condition += f" and pi.supplier_group IN {total_group}"
            else:
                total_group = supplier_group[0]['name']
                condition += f" and pi.supplier_group = '{total_group}'"
                
        if filters['supplier_group']:
            supplier_group = filters["supplier_group"][0]
            condition += f" and pi.supplier_group = '{supplier_group}'"
        
        if filters['supplier']:
            supplier = filters["supplier"][0]
            condition += f" and pi.supplier = '{supplier}'"
            
        return condition

def get_data(filters,result_condtions):
    if filters.type_of_tree == "Supplier Wise":
        data = frappe.db.sql("""select supplier,supplier_name,supplier_group,sum(grand_total) as grand_total,sum(base_net_total) as taxable_amount
                        from `tabPurchase Invoice` Where docstatus = 1  and is_return != 1 and {conditions} Group by supplier """.format(conditions=result_condtions),as_dict =1)
        
        date = f"posting_date Between'{filters.from_date}' and '{filters.to_date}'"
        for i in data:
            data_return = frappe.db.sql("""select supplier,supplier_name,supplier_group,sum(grand_total) as return_amount,sum(base_net_total) as taxable_return_amount
                            from `tabPurchase Invoice` Where docstatus = 1  and is_return = 1 and supplier = '{conditions}' and {date} Group by supplier ORDER BY supplier """.format(conditions=i["supplier"],date =date),as_dict =1)
            
            if len(data_return)>0:
                parent_supplier_group = frappe.db.sql("""select parent_supplier_group from `tabSupplier Group` where name = '{}' """.format(i.supplier_group),as_dict=1)
                i['parent_supplier_group'] = parent_supplier_group[0]["parent_supplier_group"]
                i["return_amount"] = data_return[0]["return_amount"]
                i["taxable_return_amount"] = data_return[0]["taxable_return_amount"]
                i['taxable_total_amount'] = flt(i["taxable_amount"] + data_return[0]["taxable_return_amount"])
                i["total_amount"] = flt(i['grand_total'] + data_return[0]['return_amount'])
                
            if not len(data_return)>0:
                parent_customer_group = frappe.db.sql("""select parent_supplier_group from `tabSupplier Group` where name = '{}' """.format(i.supplier_group),as_dict=1)
                i['parent_supplier_group'] = parent_customer_group[0]["parent_supplier_group"]
                i["total_amount"] = flt(i['grand_total'])
                i["taxable_total_amount"] = flt(i['taxable_amount'])
        
        return data
    if filters.type_of_tree == "Item Wise":
        
        data = frappe.db.sql("""select pi.supplier,pi.supplier_group,pi.supplier_name,poi.item_code,poi.item_group,poi.item_name,SUM(amount) as amount,SUM(stock_qty) as qty
                             FROM
                             `tabPurchase Invoice` as pi,
                             `tabPurchase Invoice Item` as poi
                             WHERE
                             poi.parent = pi.name and
                             pi.docstatus = 1  and pi.is_return != 1 and {conditions}
                             GROUP BY
                             pi.supplier,poi.item_code
                             """.format(conditions=result_condtions),as_dict=1)

        if len(data)>0:
            for i in data:
                parent_item_group = frappe.db.sql("""select parent_item_group from `tabItem Group` where name = '{}' """.format(i.item_group),as_dict=1)
                parent_customer_group = frappe.db.sql("""select parent_supplier_group from `tabSupplier Group` where name = '{}' """.format(i.supplier_group),as_dict=1)
                i['parent_supplier_group'] = parent_customer_group[0]["parent_supplier_group"]
                i['parent_item_group'] = parent_item_group[0]['parent_item_group']
                
        return data
    
    if filters.type_of_tree == "Item Group Wise":
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group_wise = frappe.db.sql("""select name from `tabItem Group` where parent_item_group = '{}' """.format(parent_group),as_dict=1)
            if len(item_group_wise)>2: 
                data = tuple([i["name"] for i in item_group_wise])
                name = f"and poi.item_group IN {data}"
            else:
                name = f"and poi.item_group ='{item_group_wise[0]['name']}'"
            data = frappe.db.sql("""select pi.supplier,pi.supplier_group,poi.item_group,SUM(poi.amount) as amount from `tabPurchase Invoice` as pi,`tabPurchase Invoice Item` as poi Where poi.parent = pi.name and
                                pi.docstatus = 1 {name} and {condition}
                                Group By poi.item_group ,pi.supplier_group , pi.supplier ORDER BY pi.supplier""".format(name=name,condition=result_condtions), as_dict=1)
            if len(data) >0:
                data_1 = []
                for i in data:
                    value = {}
                    value['supplier'] = i.get('supplier')
                    value['supplier_group'] = i.get('supplier_group')
                    value[i.get('item_group')] = i.get("amount")
                    value['total'] = i.get("amount")
                    data_1.append(value)
                    
                data_convert = pd.DataFrame.from_records(data_1,)
                final_data = data_convert.groupby(['supplier',"supplier_group"],as_index=False).sum()
                convert_data = final_data.to_dict('records')
                return convert_data
    
    if filters.type_of_tree == "Item Group Wise Qty":
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group_wise = frappe.db.sql("""select name from `tabItem Group` where parent_item_group = '{}' """.format(parent_group),as_dict=1)
            if len(item_group_wise)>2: 
                data = tuple([i["name"] for i in item_group_wise])
                name = f"and poi.item_group IN {data}"
            else:
                name = f"and poi.item_group ='{item_group_wise[0]['name']}'"
                
            data = frappe.db.sql("""select pi.supplier,pi.supplier_group,poi.item_group,SUM(poi.stock_qty) as qty from `tabPurchase Invoice` as pi,`tabPurchase Invoice Item` as poi Where poi.parent = pi.name and
                                pi.docstatus = 1 {name} and {condition}
                                Group By poi.item_group ,pi.supplier_group , pi.supplier ORDER BY pi.supplier""".format(name=name,condition=result_condtions), as_dict=1)
            if len(data) >0:
                data_1 = []
                for i in data:
                    value = {}
                    value['supplier'] = i.get('supplier')
                    value['supplier_group'] = i.get('supplier_group')
                    value[i.get('item_group')] = i.get("qty")
                    value['total_qty'] = i.get("qty")
                    data_1.append(value)
                    
                data_convert = pd.DataFrame.from_records(data_1,)
                final_data = data_convert.groupby(['supplier',"supplier_group"],as_index=False).sum()
                convert_data = final_data.to_dict('records')
                return convert_data
            
    
    
def get_columns(filters):
    columns = []
    if filters.type_of_tree == 'Supplier Wise' or filters.type_of_tree == 'Item Wise':
        columns += [
            {
                "label": _("Supplier"),
                "fieldname": "supplier",
                "fieldtype": "Link",
                "options": "Customer",
                "width": 150,
            },
            {
                "label": _("Supplier Name"),
                "fieldname": "supplier_name",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Parent Supplier Group"),
                "fieldname": "parent_supplier_group",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Supplier Group"),
                "fieldname": "supplier_group",
                "fieldtype": "Data",
                "width": 150,
            }
    ]
    if filters.type_of_tree == 'Supplier Wise':
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
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 150,
        },
        ]
    if filters.type_of_tree == 'Item Group Wise' and filters['item_parent_Group']:
        columns +=[
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
        },
        {
            "label": _("Supplier Group"),
            "fieldname": "supplier_group",
            "fieldtype": "Data",
            "width": 150,
        },
        ]
        if filters['item_parent_Group']:
            parent_group = filters['item_parent_Group'][0]
            item_group = frappe.db.get_list("Item Group",{"parent_item_group":parent_group},pluck='name')
        columns += [{"label": _(each),"fieldname": each, "fieldtype": "Currency", "width": 150} for each in item_group]
        columns +=[{"label":_("Total"),"fieldname":"total","fieldtype":"Currency","width":150}]
        
    if filters.type_of_tree == 'Item Group Wise Qty' and filters['item_parent_Group']:
        columns +=[
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
        },
        {
            "label": _("Supplier Group"),
            "fieldname": "supplier_group",
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