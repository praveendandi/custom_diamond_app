# Copyright (c) 2023, Ganu Reddy and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



from collections import OrderedDict

import frappe
from frappe import _, qb
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	# columns, data = [], []
	# return columns, data

	if not filters:
		return [], [], None, []

	validate_filters(filters)
	columns = get_columns(filters)
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)
	so_elapsed_time = get_so_elapsed_time(data)

	if not data:
		return [], [], None, []

	data, chart_data = prepare_data(data, so_elapsed_time, filters)

	return columns, data, None, chart_data


def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date and to_date:
		frappe.throw(_("From and To Dates are required."))
	elif date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))


def get_conditions(filters):
	# print(filters,'--------------')
	conditions = ""

	conditions += f" and so.transaction_date between'{filters.from_date}' and '{filters.to_date}'"

	if filters.get("company"):
		conditions += " and so.company = %(company)s"

	# if filters.get("sales_order"):
	# 	conditions += " and so.name in %(sales_order)s"
	
	if filters.get("customer"):
		conditions += " and so.customer in %(customer)s"
	
	if filters.get("customer_group"):
		conditions += " and so.customer_group in %(customer_group)s"

	if filters.get("parent_customer_group") and not filters.get("customer_group"):
		parent_group = frappe.db.get_list("Customer Group",{'parent_customer_group':filters.get("parent_customer_group")[0]},pluck ='name')
		data = tuple(parent_group)
		conditions +=f" and so.customer_group IN {data}"
		# conditions +=f" and cg.parent_customer_group in %(parent_customer_group)s"


	if filters.get("parent_item_group") and not filters.get("item_group"):
		parent_group = frappe.db.get_list("Item Group",{'parent_item_group':filters.get("parent_item_group")[0]},pluck ='name')
		data = tuple(parent_group)
		conditions +=f" and soi.item_group IN {data}"

	if filters.get("item_group"):
		conditions += " and soi.item_group in %(item_group)s"

	if filters.get("item_code"):
		conditions += " and soi.item_code in %(item_code)s"

	# if filters.get("status"):
	# 	conditions += " and so.status in %(status)s"

	return conditions


def get_data(conditions, filters):
	data = frappe.db.sql(
		"""
		SELECT
			so.name as sales_order,so.status, so.customer,so.customer_group,soi.item_code,soi.item_group,
			SUM(soi.qty) AS qty, SUM(soi.delivered_qty) AS delivered_qty,(SUM(soi.qty) - SUM(soi.delivered_qty)) AS pending_qty,
			dn.name as delivery_note,
			so.company, soi.name,
			soi.description as description
		FROM
			`tabSales Order` so
			INNER JOIN `tabSales Order Item` soi ON soi.parent = so.name
            LEFT JOIN `tabDelivery Note Item` dni ON dni.so_detail = soi.name
            LEFT JOIN `tabDelivery Note` dn ON dni.parent = dn.name
	
		WHERE
			soi.parent = so.name
			and so.status not in ('Stopped', 'Closed', 'On Hold')
			and so.docstatus = 1
			{conditions}
		GROUP BY so.customer,soi.item_code
		ORDER BY so.transaction_date ASC, soi.item_code ASC,soi.item_group ASC
	""".format(
			conditions=conditions
		),
		filters,
		as_dict=1,
	)

	for i in data:
		parent_customer_group = frappe.db.get_list("Customer Group",{"name":i.customer_group},["parent_customer_group"])
		if parent_customer_group:
			i["parent_customer_group"] = parent_customer_group[0]['parent_customer_group']
			
		parent_item_group = frappe.db.get_list("Item Group",{"name":i.item_group},["parent_item_group"])
		if parent_item_group:
			i["parent_item_group"] = parent_item_group[0]['parent_item_group']
	# print(data,'//////////////////////')
	return data
	


def get_so_elapsed_time(data):
	"""
	query SO's elapsed time till latest delivery note
	"""
	so_elapsed_time = OrderedDict()
	if data:
		sales_orders = [x.sales_order for x in data]

		so = qb.DocType("Sales Order")
		soi = qb.DocType("Sales Order Item")
		dn = qb.DocType("Delivery Note")
		dni = qb.DocType("Delivery Note Item")

		to_seconds = CustomFunction("TO_SECONDS", ["date"])

		query = (
			qb.from_(so)
			.inner_join(soi)
			.on(soi.parent == so.name)
			.left_join(dni)
			.on(dni.so_detail == soi.name)
			.left_join(dn)
			.on(dni.parent == dn.name)
			.select(
				so.name.as_("sales_order"),
				soi.item_code.as_("so_item_code"),
				(to_seconds(Max(dn.posting_date)) - to_seconds(so.transaction_date)).as_("elapsed_seconds"),
			)
			.where((so.name.isin(sales_orders)) & (dn.docstatus == 1))
			.orderby(so.name, soi.name)
			.groupby(soi.name)
		)
		dn_elapsed_time = query.run(as_dict=True)

		for e in dn_elapsed_time:
			key = (e.sales_order, e.so_item_code)
			so_elapsed_time[key] = e.elapsed_seconds

	return so_elapsed_time


def prepare_data(data, so_elapsed_time, filters):
	completed, pending = 0, 0

	if filters.get("group_by_so"):
		sales_order_map = {}

	for row in data:
		# completed += row["billed_amount"]
		# pending += row["pending_amount"]

		# row["qty_to_bill"] = flt(row["qty"]) - flt(row["billed_qty"])

		# row["delay"] = 0 if row["delay"] and row["delay"] < 0 else row["delay"]

		row["time_taken_to_deliver"] = (
			so_elapsed_time.get((row.sales_order, row.item_code))
			if row["status"] in ("To Bill", "Completed")
			else 0
		)

		if filters.get("group_by_so"):
			so_name = row["sales_order"]

			if not so_name in sales_order_map:
				row_copy = copy.deepcopy(row)
				sales_order_map[so_name] = row_copy
			else:
				so_row = sales_order_map[so_name]
				so_row["required_date"] = max(getdate(so_row["delivery_date"]), getdate(row["delivery_date"]))
				# so_row["delay"] = min(so_row["delay"], row["delay"])

				fields = [
					"qty",
					"delivered_qty",
					"pending_qty",
					"billed_qty",
					"qty_to_bill",
					"amount",
					"delivered_qty_amount",
					"billed_amount",
					"pending_amount",
				]
				for field in fields:
					so_row[field] = flt(row[field]) + flt(so_row[field])

	chart_data = prepare_chart_data(pending, completed)

	if filters.get("group_by_so"):
		data = []
		for so in sales_order_map:
			data.append(sales_order_map[so])
		return data	 	#chart_data

	return data, chart_data


def prepare_chart_data(pending, completed):
	pass
	# labels = ["Amount to Bill", "Billed Amount"]

	# return {
	# 	"data": {"labels": labels, "datasets": [{"values": [pending, completed]}]},
	# 	"type": "donut",
	# 	"height": 300,
	# }


def get_columns(filters):
	columns = [

		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 130,
		},
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 130,
		},
		
		{
			"label": _("Parent Customer Group"),
			"fieldname": "parent_customer_group",
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 130,
			"is_group":1
		},
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 130,
		},
		{
			"label": _("Delivery Note"),
			"fieldname": "delivery_note",
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 130,
		},
	]

	if not filters.get("group_by_so"):
		columns.append(
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 100,
			}
		)


	columns.extend(
		[
			{
				"label": _("Item Group"),
				"fieldname": "item_group",
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 100,
				
			},
			{
				"label": _("Parent Item Group"),
				"fieldname": "parent_item_group",
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 100,
				"is_group":1
			},
			{
				"label": _("Ordered Qty"),
				"fieldname": "qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			{
				"label": _("Delivered Qty"),
				"fieldname": "delivered_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},
			
			{
				"label": _("Short Qty"),
				"fieldname": "pending_qty",
				"fieldtype": "Float",
				"width": 120,
				"convertible": "qty",
			},


		]
	)

	return columns

