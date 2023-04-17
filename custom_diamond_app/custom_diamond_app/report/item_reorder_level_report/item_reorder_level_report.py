# Copyright (c) 2023, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    data = get_date(filters)
    columns = get_columns(filters)
    return columns, data

def get_conditions(filters):
    condition = ''
    if filters.type_of_tree == 'Item Wise':
        items = frappe.db.get_list('Item',['item_code','item_name'])
        name = tuple([i["item_code"] for i in items])
        condition += f" and i.item_code IN {name}"
    # if filters.warehouse:
    #     condition += f" and w.warehouse = '{filters.warehouse}'"

    return condition

def get_date(filters):
    conditions = get_conditions(filters)

    item_details = frappe.db.sql('''Select i.item_code,i.item_name,i.item_group,io.warehouse as reorder_warehouse,
                                    io.warehouse_reorder_level as reorder_level from `tabItem` as i,
                                    `tabItem Reorder` as io Where io.parent = i.item_code {condition} Group By item_code
                                    '''.format(condition= conditions),as_dict =1)
    
    for i in item_details:
        total_qty = 0.0
        warehouse_qty = frappe.db.sql('''Select item_code,SUM(actual_qty) as qty ,warehouse from `tabStock Ledger Entry` Where item_code = '{item}' Group By warehouse '''.format(item = i['item_code']),as_dict=1)
        if len(warehouse_qty) > 0:
            for j in warehouse_qty:
                warehouse_name = j["warehouse"]
                qty = j["qty"]
                i[warehouse_name] = qty
                total_qty +=qty
                i['total_qty'] = total_qty
    
    for k in item_details:
        if 'total_qty' in k:
            if k['total_qty'] < k['reorder_level']:
                k['short_qty'] = k['reorder_level'] - k['total_qty']  
    
    return item_details


def get_columns(filters):
    columns = []
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
            "label": _("Reorder Warehouse"),
            "fieldname": "reorder_warehouse",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Reorder Level"),
            "fieldname": "reorder_level",
            "fieldtype": "Data",
            "width": 150,
        },
        
    ]
    item_group = frappe.db.get_list("Warehouse",{"parent_warehouse":'All Warehouses - DMPL','disabled':0},pluck='name')
    columns += [{"label": _(each),"fieldname": each, "fieldtype": "Data", "width": 150} for each in item_group]
    columns +=[{"label":_("Total Qty"),"fieldname":"total_qty","fieldtype":"Data","width":150}]
    columns +=[{"label":_("Short Qty"),"fieldname":"short_qty","fieldtype":"Data","width":150}]


    return columns
