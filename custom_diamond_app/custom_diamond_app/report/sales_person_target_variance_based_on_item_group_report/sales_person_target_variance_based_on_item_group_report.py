# Copyright (c) 2022, kiran and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


from __future__ import unicode_literals
import numbers
import frappe
from frappe import _, msgprint
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges
import pandas as pd

def execute(filters=None):
    if not filters: filters = {}

    columns = get_columns(filters)
    period_month_ranges = get_period_month_ranges(filters["period"], filters["fiscal_year"])
    sim_map = get_salesperson_item_month_map(filters)
    data = []
    status = False
    user_mail = frappe.session.user
    user_details = frappe.db.get_value("User", {"name": user_mail}, ["full_name"])
    role_doc = frappe.db.get_list("Has Role", filters=[["parent","=",user_mail]], fields=["role"])
    for each in role_doc:
        if each["role"] == "System Manager":
            status = True
    for salesperson, salesperson_items in sim_map.items():
        if not status:
            if user_details != salesperson:
                continue
        for item_group, monthwise_data in salesperson_items.items():
            row = [salesperson, item_group]
            totals = [0, 0, 0]
            for relevant_months in period_month_ranges:
                period_data = [0, 0, 0]
                for month in relevant_months:
                    month_data = monthwise_data.get(month, {})
                    for i, fieldname in enumerate(["target", "achieved", "variance"]):
                        value = flt(month_data.get(fieldname))
                        period_data[i] += value
                        totals[i] += value
                period_data[2] = period_data[0] - period_data[1]
                row += period_data
            totals[2] = totals[0] - totals[1]
            row += totals
            data.append(row)

    if len(data) > 0:
        df = pd.DataFrame(data=data, columns=columns)
        totals = dict(df.sum(numeric_only=True))
        totals["Sales Person:Link/Sales Person:120"] = "Total"
        totals["Item Group:Link/Item Group:120"] = ""
        total = {}
        for each in columns:
            total.update({each:totals[each]})
        data.append(list(total.values()))
    return columns, sorted(data, key=lambda x: (x[0], x[1]))        
   
    


def get_columns(filters):
    for fieldname in ["fiscal_year", "period", "target_on"]:
        if not filters.get(fieldname):
            label = (" ".join(fieldname.split("_"))).title()
            msgprint(_("Please specify") + ": " + label,
                raise_exception=True)

    columns = [_("Sales Person") + ":Link/Sales Person:120", _("Item Group") + ":Link/Item Group:120"]

    group_months = False if filters["period"] == "Monthly" else True

    for from_date, to_date in get_period_date_ranges(filters["period"], filters["fiscal_year"]):
        for label in [_("Target") + " (%s)", _("Achieved") + " (%s)", _("Variance") + " (%s)"]:
            if group_months:
                label = label % (_(from_date.strftime("%b")) + " - " + _(to_date.strftime("%b")))
            else:
                label = label % _(from_date.strftime("%b"))

            columns.append(label+":Float:120")

    return columns + [_("Total Target") + ":Float:120", _("Total Achieved") + ":Float:120",
        _("Total Variance") + ":Float:120"]

#Get sales person & item group details
def get_salesperson_details(filters):
    return frappe.db.sql("""
        select
            sp.name, td.item_group, td.target_qty, td.target_amount
        from
            `tabSales Person` sp, `tabTarget Detail` td
        where
            td.parent=sp.name and td.fiscal_year=%s order by sp.name
        """, (filters["fiscal_year"]), as_dict=1)

#Get target distribution details of item group
def get_target_distribution_details(filters):
    target_details = {}

    for d in frappe.db.sql("""
        select
            md.name, mdp.month, mdp.percentage_allocation
        from
            `tabMonthly Distribution Percentage` mdp, `tabMonthly Distribution` md
        where
            mdp.parent=md.name and md.fiscal_year=%s
        """, (filters["fiscal_year"]), as_dict=1):
            target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))

    return target_details

#Get achieved details from sales order
def get_achieved_details(filters, sales_person, all_sales_persons, target_item_group, item_groups):
    start_date, end_date = get_fiscal_year(fiscal_year = filters["fiscal_year"])[1:]
    if filters['doctype']=="Sales Invoice":
        item_details = frappe.db.sql("""
                select
                        sum(sii.stock_qty * (st.allocated_percentage/100)) as qty,
                        sum(sii.base_net_amount * (st.allocated_percentage/100)) as amount,
                        st.sales_person, MONTHNAME(si.creation) as month_name
                from
                        `tabSales Invoice Item` sii, `tabSales Invoice` si, `tabSales Team` st
                where
                        sii.parent=si.name and si.docstatus=1 and st.parent=si.name
                        and si.creation>=%s and si.creation<=%s
                        and exists(select name from `tabSales Person` where lft >= %s and rgt <= %s and name=st.sales_person)
                        and exists(select name from `tabItem Group` where lft >= %s and rgt <= %s and name=sii.item_group)
                group by
                        sales_person, month_name
                        """,
                (start_date, end_date, all_sales_persons[sales_person].lft, all_sales_persons[sales_person].rgt,
                        item_groups[target_item_group].lft, item_groups[target_item_group].rgt), as_dict=1)

        actual_details = {}
        for d in item_details:
            actual_details.setdefault(d.month_name, frappe._dict({
                    "quantity" : 0,
                    "amount" : 0
            }))

            value_dict = actual_details[d.month_name]
            value_dict.quantity += flt(d.qty)
            value_dict.amount += flt(d.amount)

        return actual_details

    if filters['doctype']=="Sales Order":
        item_detail = frappe.db.sql("""select soi.item_code, soi.qty, soi.base_net_amount, so.transaction_date,
        st.sales_person, MONTHNAME(so.transaction_date) as month_name
            from `tabSales Order Item` soi, `tabSales Order` so, `tabSales Team` st
            where soi.parent=so.name and so.docstatus=1 and
            st.parent=so.name and so.transaction_date>=%s and
            so.transaction_date<=%s and so.owner = %s and exists(select name from `tabSales Person` where lft >= %s and rgt <= %s and name=st.sales_person)
                        and exists(select name from `tabItem Group` where lft >= %s and rgt <= %s and name=soi.item_group) group by sales_person, month_name""",
            (start_date, end_date, frappe.session.user, all_sales_persons[sales_person].lft, all_sales_persons[sales_person].rgt,
                        item_groups[target_item_group].lft, item_groups[target_item_group].rgt), as_dict=1)
        actual_detail = {}
        for d in item_detail:
            actual_detail.setdefault(d.month_name, frappe._dict({
                    "quantity" : 0,
                    "amount" : 0
            }))

            value_dict = actual_detail[d.month_name]
            value_dict.quantity += flt(d.qty)
            value_dict.amount += flt(d.base_net_amount)
        return actual_detail
    if filters['doctype']=="Delivery Note":
        item_detail_del = frappe.db.sql("""select soi.item_code, soi.qty, soi.base_net_amount, so.creation,
        st.sales_person, MONTHNAME(so.creation) as month_name
            from `tabDelivery Note Item` soi, `tabDelivery Note` so, `tabSales Team` st
            where soi.parent=so.name and so.docstatus=1 and
            st.parent=so.name and so.creation>=%s and
            so.creation<=%s and exists(select name from `tabSales Person` where lft >= %s and rgt <= %s and name=st.sales_person)
                        and exists(select name from `tabItem Group` where lft >= %s and rgt <= %s and name=soi.item_group) group by sales_person, month_name""",
            (start_date, end_date, all_sales_persons[sales_person].lft, all_sales_persons[sales_person].rgt,
                        item_groups[target_item_group].lft, item_groups[target_item_group].rgt), as_dict=1)
        actual_detail_del = {}
        for d in item_detail_del:
            actual_detail_del.setdefault(d.month_name, frappe._dict({
                    "quantity" : 0,
                    "amount" : 0
            }))

            value_dict = actual_detail_del[d.month_name]
            value_dict.quantity += flt(d.qty)
            value_dict.amount += flt(d.base_net_amount)
        return actual_detail_del

def get_salesperson_item_month_map(filters):
    import datetime
    salesperson_details = get_salesperson_details(filters)
    tdd = get_target_distribution_details(filters)
    item_groups = get_item_groups()
    sales_persons = get_sales_persons()
    sales_person_achievement_dict = {}
    for sd in salesperson_details:
        achieved_details = get_achieved_details(filters, sd.name, sales_persons, sd.item_group, item_groups)

        for month_id in range(1, 13):
            month = datetime.date(2013, month_id, 1).strftime('%B')
            sales_person_achievement_dict.setdefault(sd.name, {}).setdefault(sd.item_group, {})\
                    .setdefault(month, frappe._dict({
                            "target": 0.0, "achieved": 0.0
                        }))
            sales_target_achieved = sales_person_achievement_dict[sd.name][sd.item_group][month]
            month_percentage = tdd.get(sd.distribution_id, {}).get(month, 0) \
                if sd.distribution_id else 100.0/12

            if (filters["target_on"] == "Quantity"):
                sales_target_achieved.target = flt(sd.target_qty) * month_percentage / 100
            else:
                sales_target_achieved.target = flt(sd.target_amount) * month_percentage / 100

            sales_target_achieved.achieved = achieved_details.get(month, frappe._dict())\
                .get(filters["target_on"].lower())
    return sales_person_achievement_dict

def get_item_groups():
    item_groups = frappe._dict()
    for d in frappe.get_all("Item Group", fields=["name", "lft", "rgt"]):
        item_groups.setdefault(d.name, frappe._dict({
            "lft": d.lft,
            "rgt": d.rgt
        }))
    return item_groups

def get_sales_persons():
    sales_persons = frappe._dict()
    for d in frappe.get_all("Sales Person", fields=["name", "lft", "rgt"]):
        sales_persons.setdefault(d.name, frappe._dict({
            "lft": d.lft,
            "rgt": d.rgt
        }))
    return sales_persons
