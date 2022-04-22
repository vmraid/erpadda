vmraid.provide('erpadda.PointOfSale');

vmraid.pages['point-of-sale'].on_page_load = function(wrapper) {
	vmraid.ui.make_app_page({
		parent: wrapper,
		title: __('Point of Sale'),
		single_column: true
	});

	vmraid.require('point-of-sale.bundle.js', function() {
		wrapper.pos = new erpadda.PointOfSale.Controller(wrapper);
		window.cur_pos = wrapper.pos;
	});
};

vmraid.pages['point-of-sale'].refresh = function(wrapper) {
	if (document.scannerDetectionData) {
		onScan.detachFrom(document);
		wrapper.pos.wrapper.html("");
		wrapper.pos.check_opening_entry();
	}
};
