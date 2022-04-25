frappe.ui.form.on("Item", "refresh", function(frm) {
    console.log("////////?////////")
    frappe.db.get_value("Item", {'name':frm.doc.name}, ['*']).then(response => {
        frappe.route_options = {"gst_hsn_code": frm.doc.gst_hsn_code};
        frappe.set_route("Item", frm.doc.name);   
    });
    });