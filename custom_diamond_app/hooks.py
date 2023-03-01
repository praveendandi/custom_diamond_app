from . import __version__ as app_version

app_name = "custom_diamond_app"
app_title = "Custom Diamond App"
app_publisher = "kiran"
app_description = "diamond "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "kiran@caratred.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_diamond_app/css/custom_diamond_app.css"
# app_include_js = "/assets/custom_diamond_app/js/custom_diamond_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_diamond_app/css/custom_diamond_app.css"
# web_include_js = "/assets/custom_diamond_app/js/custom_diamond_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "custom_diamond_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
fixtures = [
    {
        "dt":
        "Custom Field",
        "filters": [[
            "name",
            "in",
            [
                'Sales Invoice-single_carton',
                'Sales Invoice-double_carton',
                'Sales Invoice-total_no_of_carton',
                'Sales Order Item-additional_customer_discount',
                'Sales Invoice Item-additional_customer_discount',
                'Delivery Note Item-quantity_in_sales_order_',
                'Item Price-item_group',
                'Delivery Note Item-packed_quantity',
                'Delivery Note-customer_discount_category',
                'Delivery Note Item-additional_customer_discount',
                'Purchase Order-supplier_group',
                'Purchase Receipt-supplier_group',
                'Purchase Invoice-supplier_group',
                'Delivery Note Item-check',
                'Sales Order-item_category',
                'Sales Order-narration',
                'Delivery Note-item_category',
                'Delivery Note-single_carton',
                'Delivery Note-double_carton',
                'Delivery Note-total_no_of_carton',
                'Sales Invoice-lc_copy',
                'Purchase Invoice-bill_copy',
                'Delivery Note-narration',
                'Sales Invoice-narration',
                'Customer-transporter_name',
                'Customer-name_of_transporter_',
                'Customer-transporter_gstn',
                'Sales Invoice-name_of_transporter_',
                'Sales Invoice-transporter_gstn',
                'Bank Account-branch',
                # 'Sales Order-transporter_id',
                ]
        ]]
    },
]
# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_diamond_app.install.before_install"
# after_install = "custom_diamond_app.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_diamond_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"on_update": "custom_diamond_app.events.update_item_details_erp",
	},
  	"Sales Order": {
		"on_submit":"custom_diamond_app.events.sales_order_overdue_validation",
	},
   "Purchase Receipt": {
        "before_submit":"custom_diamond_app.events.stock_entry_after_submit_purchase_recipt"
    },
    "BOM":{
        "on_update":"custom_diamond_app.events.bom_item_uom"
    },
    'Payment Entry':{
        'on_update':'custom_diamond_app.events.posting_date'
    }
}	

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_diamond_app.tasks.all"
# 	],
# 	"daily": [
# 		"custom_diamond_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_diamond_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_diamond_app.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_diamond_app.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_diamond_app.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_diamond_app.event.get_events"
# }
override_whitelisted_methods = {
    "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note":"custom_diamond_app.events.make_delivery_note"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "custom_diamond_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"custom_diamond_app.auth.validate"
# ]

