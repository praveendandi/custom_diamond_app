# Copyright (c) 2022, kiran and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.utils import today
from frappe import _, scrub
from frappe.utils import cint, flt
from six import iteritems

from erpnext.accounts.party import get_partywise_advanced_payment_amount
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport
from erpnext.accounts.doctype.bank_account import bank_account
from datetime import date

def execute(filters=None):
	args = {
		"party_type": "Customer",
		"naming_by": ["Selling Settings", "cust_master_name"],
	}

	return AccountsReceivableSummary(filters).run(args)


class AccountsReceivableSummary(ReceivablePayableReport):
	def run(self, args):
		self.party_type = args.get("party_type")
		self.party_naming_by = frappe.db.get_value(
			args.get("naming_by")[0], None, args.get("naming_by")[1]
		)
		
		self.get_columns()
		self.get_data(args)
		# print(self.data,"/////////////////////////////////////////")
		return self.columns, self.data

	def get_data(self, args):
		self.data = []
		self.receivables = ReceivablePayableReport(self.filters).run(args)[1]
		self.get_party_total(args)
		party_advance_amount = (
			get_partywise_advanced_payment_amount(
				self.party_type,
				self.filters.report_date,
				self.filters.show_future_payments,
				self.filters.company,
			)
			or {}
		)
		

		if self.filters.show_gl_balance:
			gl_balance_map = get_gl_balance(self.filters.report_date)

		for party, party_dict in iteritems(self.party_total):
			if party_dict.outstanding == 0:
				continue

			row = frappe._dict()
			
			row.party = party
			if self.party_naming_by == "Naming Series":
				row.party_name = frappe.get_cached_value(
					self.party_type, party, scrub(self.party_type) + "_name"
				)
			acc = frappe.db.sql(
				"""select account_name,bank,branch_code,bank_account_no as bank_account_number,party from `tabBank Account` where party = '{0}'
				""".format(party),
				as_dict=1,	
				)
			if acc:
				row.update(acc[0])

			row.update(party_dict)

			# Advance against party
			row.advance = party_advance_amount.get(party, 0)
			# export_date = []
			if self.filters.show_gl_balance:
				row.gl_balance = gl_balance_map.get(party)
				row.diff = flt(row.outstanding) - flt(row.gl_balance)
				# row.export_date = frappe.utils.formatdate(today(), "dd-MM-yyyy")
				# print(export_date,"000000000000000000000000")
			self.data.append(row)

	def get_party_total(self, args):
		self.party_total = frappe._dict()
		for d in self.receivables:
			self.init_party_total(d)


			# Add all amount columns
			for k in list(self.party_total[d.party]):
				if k not in ["currency", "sales_person"]:
					self.party_total[d.party][k] += d.get(k, 0.0)


	def init_party_total(self, row):
		self.party_total.setdefault(
			row.party,
			frappe._dict(
				{
					"outstanding": 0.0,
				},
			),
		)
                                        	
	def get_columns(self):
		self.columns = []
		if self.party_naming_by == "Naming Series":
			self.add_column(_("Bank Account Number"),fieldname="bank_account_number", fieldtype="Int")
			self.add_column(_("Amount"), fieldname="outstanding")
			self.add_column(_("Account Name"),fieldname="account_name", fieldtype="Link")
			self.add_column(_("{0} Name").format(self.party_type), fieldname="party_name", fieldtype="Data")
			self.add_column(label=_(self.party_type),fieldname="party",fieldtype="Link",
						options=self.party_type,width=180,)
			self.add_column(_("Export date"))
			self.add_column(_("Branch Code"), fieldname="branch_code", fieldtype="Data")
			self.add_column(_("Bank"),fieldname="bank", fieldtype="Data")
			# self.add_column(_("Email Id"), fieldname="email_id", fieldtype="Data")
			# self.add_column(_("Account Name"),fieldname="account_name", fieldtype="Data")

		if self.filters.show_sales_person:
			self.add_column(label=_("Sales Person"), fieldname="sales_person", fieldtype="Data")
		

def get_gl_balance(report_date):
	return frappe._dict(
		frappe.db.get_all(
			"GL Entry",
			fields=["party", "sum(debit -  credit)"],
			filters={"posting_date": ("<=", report_date), "is_cancelled": 0},
			group_by="party",
			as_list=1,
		)
	)

def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return AccountsReceivableSummary(filters).run(args)
