vmraid.pages['team-updates'].on_page_load = function(wrapper) {
	var page = vmraid.ui.make_app_page({
		parent: wrapper,
		title: __('Team Updates'),
		single_column: true
	});

	vmraid.team_updates.make(page);
	vmraid.team_updates.run();

	if(vmraid.model.can_read('Daily Work Summary Group')) {
		page.add_menu_item(__('Daily Work Summary Group'), function() {
			vmraid.set_route('Form', 'Daily Work Summary Group');
		});
	}
}

vmraid.team_updates = {
	start: 0,
	make: function(page) {
		var me = vmraid.team_updates;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		me.more = $('<div class="for-more"><button class="btn btn-sm btn-default btn-more">'
			+ __("More") + '</button></div>').appendTo(me.page.main)
			.find('.btn-more').on('click', function() {
				me.start += 40;
				me.run();
			});
	},
	run: function() {
		var me = vmraid.team_updates;
		vmraid.call({
			method: 'erpadda.hr.page.team_updates.team_updates.get_data',
			args: {
				start: me.start
			},
			callback: function(r) {
				if (r.message && r.message.length > 0) {
					r.message.forEach(function(d) {
						me.add_row(d);
					});
				} else {
					vmraid.show_alert({message: __('No more updates'), indicator: 'gray'});
					me.more.parent().addClass('hidden');
				}
			}
		});
	},
	add_row: function(data) {
		var me = vmraid.team_updates;

		data.by = vmraid.user.full_name(data.sender);
		data.avatar = vmraid.avatar(data.sender);
		data.when = comment_when(data.creation);

		var date = vmraid.datetime.str_to_obj(data.creation);
		var last = me.last_feed_date;

		if((last && vmraid.datetime.obj_to_str(last) != vmraid.datetime.obj_to_str(date)) || (!last)) {
			var diff = vmraid.datetime.get_day_diff(vmraid.datetime.get_today(), vmraid.datetime.obj_to_str(date));
			var pdate;
			if(diff < 1) {
				pdate = 'Today';
			} else if(diff < 2) {
				pdate = 'Yesterday';
			} else {
				pdate = vmraid.datetime.global_date_format(date);
			}
			data.date_sep = pdate;
			data.date_class = pdate=='Today' ? "date-indicator blue" : "date-indicator";
		} else {
			data.date_sep = null;
			data.date_class = "";
		}
		me.last_feed_date = date;

		$(vmraid.render_template('team_update_row', data)).appendTo(me.body);
	}
}
