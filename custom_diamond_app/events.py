
import json
from warnings import filters

import frappe
import frappe.utils
from frappe import _
from frappe.contacts.doctype.address.address import get_company_address
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from six import string_types

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


def update_addition_discount(doc,method=None):
    print(doc,doc.items[0].additional_customer_discount,doc.customer_discount_category,";;;;;;;;;;;;;;;;")
    # print(doc,doc.pricing_rules[0].item_code,doc.pricing_rules[0].pricing_rule,"////////////////")
    discount = doc.items[0].additional_customer_discount
    item_groups = None
    
    for i in doc.pricing_rules:
        item_value = i.item_code
        pricing_value = i.pricing_rule
        if frappe.db.exists("Pricing Rule", {"name": pricing_value,'sytem_generated':'Yes'}):
            frappe.db.set_value('Pricing Rule',pricing_value,{'discount_percentage':discount})
            frappe.db.commit()
            
            item_groups = frappe.db.sql('''select item_group from `tabPricing Rule Item Group` Where parent = '{}' '''.format(pricing_value),as_dict=1)
            
    if item_groups:
        item_group = item_groups[0].get('item_group')
        discount_defini = doc.customer_discount_category   
        frappe.db.set_value('Discount Definitions Item',{'parent':discount_defini,'item_group':item_group},{'amount':discount})
        frappe.db.commit()