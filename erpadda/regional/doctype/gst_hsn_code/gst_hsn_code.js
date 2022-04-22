// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('GST HSN Code', {
	refresh: function(frm) {
		if(! frm.doc.__islocal && frm.doc.taxes.length){
			frm.add_custom_button(__('Update Taxes for Items'), function(){
				vmraid.confirm(
					'Are you sure? It will overwrite taxes for all items with HSN Code <b>'+frm.doc.name+'</b>.',
					function(){
						vmraid.call({
							args:{
								taxes: frm.doc.taxes,
								hsn_code: frm.doc.name
							},
							method: 'erpadda.regional.doctype.gst_hsn_code.gst_hsn_code.update_taxes_in_item_master',
							callback: function(r) {
								if(r.message){
									vmraid.show_alert(__('Item taxes updated'));
								}
							}
						});
					}
				);
			});
		}
	}
});
