# Copyright (c) 2023, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.sales_register.sales_register import execute as execute_
import pandas as pd

def execute(filters=None):
    
    new_data = execute_(filters)
    
    if len(new_data[1]):
        data = get_data(filters,new_data[1])
        columns = get_columns()

        return columns, data
    else:
        [],[]


def get_data(filters,row_data):
    
    final_data = []
    for each in row_data:
        record = {}
        record.update({
            "naming_series":frappe.db.get_list("Sales Invoice",{"name":each['invoice']},['naming_series'])[0]['naming_series'],
            "net_total":each['net_total'],
            "output_tax_cgst___dmpl":each['output_tax_cgst___dmpl'],
            "output_tax_sgst___dmpl":each["output_tax_sgst___dmpl"],
            "output_tax_igst___dmpl":each['output_tax_igst___dmpl'],
            "tax_total":each['tax_total'],
            "grand_total":each['grand_total']
        })
        final_data.append(record)
        
    convert_data = pd.DataFrame.from_records(final_data)
    group_data = convert_data.groupby(by="naming_series",as_index=False).sum()
    actual_data = group_data.to_dict("records")
    
    
    for naming_ser in actual_data:
        sumbit = 0
        draft = 0
        cancel = 0
        
        sumbit = frappe.db.count('Sales Invoice', {'docstatus': 1,"naming_series":naming_ser['naming_series'],
                                                   "posting_date":[">=",filters.get("from_date"),"<=",filters.get("to_date")],
                                                   }
                            )
       
        draft = frappe.db.count('Sales Invoice', {'docstatus': 0,"naming_series":naming_ser['naming_series'],
                                                  "posting_date":[">=",filters.get("from_date")],
                                                  "posting_date":["<=",filters.get("to_date")]
                                                }
                            )

        cancel = frappe.db.count('Sales Invoice', {'docstatus': 2,"naming_series":naming_ser['naming_series'],
                                                   "posting_date":[">=",filters.get("from_date"),"<=",filters.get("to_date")],

                                                   }
                            )
        
        invoice = frappe.db.get_list("Sales Invoice",
                                     {"naming_series":naming_ser['naming_series'],
                                      "posting_date":["Between",[filters.get("from_date"),filters.get("to_date")]]
                                    },
                                    ['name','posting_date','naming_series'],
                                    order_by='posting_date asc'
                                    )
        
        first_invoice = invoice[0]['name']
        last_invoice = invoice[-1]['name']
        
        naming_ser.update({
            "first_invoice":first_invoice,
            "last_invoice":last_invoice,
            "sumbit":sumbit if sumbit >0 else 0,
            "draft":draft if draft >0 else 0,
            "cancel":cancel if cancel >0 else 0
        })
    
    return actual_data


def get_columns():
    column = [
        {
			"label": _("Namimg Series"),
			"fieldname": "naming_series",
			"fieldtype": "Data",
            "width":200,
		},
        {
			"label": _("First Invoice"),
			"fieldname": "first_invoice",
			"fieldtype": "Data",
            "width":150,
		},
        {
			"label": _("Last Invoice"),
			"fieldname": "last_invoice",
			"fieldtype": "Data",
            "width":150,
		},
        {

			"label": _("Net Totalt"),
			"fieldname": "net_total",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("CGST Amount"),
			"fieldname": "output_tax_cgst___dmpl",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("SGST Amount"),
			"fieldname": "output_tax_sgst___dmpl",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("IGST Amount"),
			"fieldname": "output_tax_igst___dmpl",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("Tax Amount"),
			"fieldname": "tax_total",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("Grand Amount"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
            "width":200,
		},
        {
			"label": _("Draft"),
			"fieldname": "draft",
			"fieldtype": "Int",
            "width":100,
		},
        {
			"label": _("Sumbit"),
			"fieldname": "sumbit",
			"fieldtype": "Int",
            "width":100,
		},
        {
			"label": _("Cancel"),
			"fieldname": "cancel",
			"fieldtype": "Int",
            "width":100,
		},
    ]
    
    return column