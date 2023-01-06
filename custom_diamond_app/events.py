
import json
from warnings import filters

import frappe
import pandas as pd
import os
from pathlib import Path
import frappe.utils
from frappe import _
from frappe.contacts.doctype.address.address import get_company_address
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from six import string_types
import time

from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.controllers.selling_controller import SellingController
from erpnext.manufacturing.doctype.production_plan.production_plan import (
	get_items_for_material_requests,
)
from erpnext.selling.doctype.customer.customer import check_credit_limit
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.get_item_details import get_default_bom
from erpnext.stock.stock_balance import get_reserved_qty, update_bin_qty
import datetime


@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
		target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
		target.qty = flt(source.qty) - flt(source.delivered_qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = (
				frappe.db.get_value("Project", source_parent.project, "cost_center")
				or item.get("buying_cost_center")
				or item_group.get("buying_cost_center")
			)

	mapper = {
		"Sales Order": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
		"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
		"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
	}

	if not skip_item_mapping:

		def condition(doc):
			# make_mapped_doc sets js `args` into `frappe.flags.args`
			if frappe.flags.args and frappe.flags.args.delivery_dates:
				if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
					return False
			return abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier != 1

		mapper["Sales Order Item"] = {
			"doctype": "Delivery Note Item",
			"field_map": {
				"rate": "rate",
				"name": "so_detail",
				"parent": "against_sales_order",
				"qty":"quantity_in_sales_order_",
			},
			"postprocess": update_item,
			"condition": condition,
		}

	target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)

	target_doc.set_onload("ignore_price_list", True)

	return target_doc

@frappe.whitelist()
def update_item_details_erp(doc,method=None):
    get_list = frappe.db.get_list("Item Price", filters={"item_code":doc.name})
    print(get_list)
    if len(get_list)>0:
        for each in get_list:
            frappe.db.set_value("Item Price", each["name"],{"Item_name":doc.item_name, "item_group":doc.item_group})
            frappe.db.commit()
            
            

            
def sales_order_overdue_validation(doc,method=None):
    print(doc,"****************************")
    get_sales_invoice = frappe.db.get_list("Sales Invoice",filters={'customer':doc.customer,'status':'overdue'},fields=['customer','status','name','grand_total','posting_date'],order_by='posting_date asc')
    print("sales invoice",get_sales_invoice)
    for invoice in get_sales_invoice:
        print(invoice["posting_date"],"*************", datetime.date.today())
        date_1 = (datetime.date.today()-invoice["posting_date"]).days
        print(date_1,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if date_1 > 90:
            frappe.db.set_value("Sales Order", doc.name, {"status":"On Hold"})
            frappe.db.commit()
            roles = get_roles(user=None,with_standard=True)
            # print(roles,"==================+++++++==========================")
            if "Customer Sales Invoices overdue 90 Days Sales order Approval" not in roles:
            # if not frappe.session.user == 'Administrator':
            # if not frappe.session.role == 'Stock User':
                frappe.throw("this customer have unpaid or overdue invoice over 90 days which is not completed, Please complete {}, or  Only this Role (Customer Sales Invoices overdue 90 Days Sales order Approval) have submit permissions".format(invoice.name))
                
        else:
            print("$$$$$$$$$$$$$$$$$")
 
            #test comment 
            #test comment 
            
def get_roles(user=None, with_standard=True):

    if not user:
        user = frappe.session.user
    if user == 'Guest':
        return ['Guest']
    def get():
        return [r[0] for r in frappe.db.sql("""select role from `tabUserRole`
            where parent=%s and role not in ('All', 'Guest')""", (user,))] + ['All', 'Guest']

    roles = frappe.cache().hget("roles", user, get)
    print(roles,"////////////////")

    if not with_standard:
        roles = filter(lambda x: x not in ['All', 'Guest', 'Administrator'], roles)
    
    print(roles,",,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    
    return roles


@frappe.whitelist()
def data_shift_api(name):
    try:
   
    
        data = frappe.db.sql("""Select customer,company,currency,conversion_rate,selling_price_list,price_list_currency,customer_discount_category
                            from `tabDelivery Note` Where name = '{name}' """.format(name=name),as_dict=1
                            )
        modify_data = []
        for i in data:
            value = {}
            if "customer" in i:
                value['Customer'] = i.get('customer')
            if "customer_discount_category" in i:
                value["Customer Discount Category"] = i.get('customer_discount_category')
            if "company" in i:
                value['Company'] = i.get('company')
            if "currency" in i:
                value['Currency'] = i.get('currency')
            if "conversion_rate" in i:
                value['Exchange Rate'] = i.get('conversion_rate')
            if 'selling_price_list' in i:
                value['Price List'] = i.get('selling_price_list')
            if 'price_list_currency' in i:
                value['Price List Currency'] = i.get('price_list_currency')
                
            modify_data.append(value)
            
    
        items_data = frappe.db.sql('''Select item_code,item_name,description,stock_qty,
                                stock_uom ,uom ,conversion_factor,additional_customer_discount from `tabDelivery Note Item`
                                Where parent = '{name}'
                                '''.format(name=name),as_dict=1)
        
        modify_items = []
        for j in items_data:
            value = {}
            if "item_code" in j:
                value["Item Code (Items)"] = j.get("item_code")
            if "item_name" in j:
                value["Item Name (Items)"] = j.get("item_name")
            if "description" in j:
                value["Description (Items)"] = j.get("description")
            if "stock_qty" in j:
                value["Packed Qty (Items)"] = j.get("stock_qty")
            if "stock_uom" in j:
                value["UOM (Items)"] = j.get("stock_uom")
            if "additional_customer_discount" in j:
                value["Additional Customer Discount (Items)"] = j.get("additional_customer_discount")
            # if "uom" in j:\
            #     value["Sales Order UOM (Items)"] = j.get("uom")
            # if "conversion_factor" in j:
            #     value["UOM Conversion Factor (Items)"] = j.get("conversion_factor")
                
            modify_data.append(value)
            
        new_data = modify_data + modify_items
        df = pd.DataFrame.from_records(new_data)
        folder_path = frappe.utils.get_bench_path()
        site_name = frappe.utils.cstr(frappe.local.site)
        xl_file_path = (folder_path+ "/sites/"+ site_name)
        file_name = f"{name}.xlsx"
        epoch = str(round(time.time() * 1000))
        file_path = '/files/'+name+epoch+".xlsx"
        serve_file_path =name+epoch+".xlsx"
        output_file_path = xl_file_path + "/public"+file_path
                        
        df.to_excel(output_file_path, index=False)
        
        return {"success":True,"file_path":file_path}
    except Exception as e:
        return {"success":False,"message":str(e)}
    
    # home_address = str(Path.home())
    
    # if not os.path.exists(home_address):
    #     os.makedirs(home_address)
    
    # path="".join("{}/{}".format(home_address, file_name))
    # df.to_excel(path, index=False)
    
    
    
    # files = name
    # # print(files,"////////////////")
    
    # file_address = f"{files}.xlsx"
    # home = str(Path.home())
    # # last_sd = "/Desktop"
    # site_loc = home+"/"+file_address
    
    
    # # print(df,"//////////////////////")
    # df.to_excel(site_loc, index=False)
    

    # print(new_data,"................................")
    
    
def stock_entry_after_submit_purchase_recipt(doc,method=None):
    if doc.is_subcontracted == "Yes":
        supplier_warehouse = doc.supplier_warehouse
        # print(supplier_warehouse,"......................")
        for i in range(len(doc.items)):
            item_codes = doc.items[i].item_code
            if frappe.db.exists("BOM",{"item":item_codes},"name"):
                print(item_codes,"////////////////")
                accepted_qty = doc.items[i].stock_qty
                print(accepted_qty,"////////////") 
                bom_no = frappe.db.get_value("BOM",{"item":item_codes},"name")
                print(bom_no,"/////////////////")
                doc_insert = frappe.get_doc("Stock Entry",{"stock_entry_type":"Material Consumption for Manufacture","from_bom":1,})
                doc_insert.bom_no = bom_no
                doc_insert.fg_completed_qty = accepted_qty
                doc_insert.get_items = 1
                doc_insert.from_warehouse = supplier_warehouse
                doc_insert.docstatus = 0
                
                doc_insert.insert()
            else:
                frappe.throw("BOM Not Exists for Item {}".format(item_codes))
        # doc_insert.submit()
