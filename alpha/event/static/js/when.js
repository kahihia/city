(function($) {
	$.widget("ui.when", {
		_create: function() {
			console.log("good");
			this.months = {
				//	2012: { 10: }
			};
			this._initDeck();
		},
		_initDeck: function() {
			var that = this,
				date = new Date()
				this.deck = $("<div>").addClass('ui-widget when-deck');
			
			this.monthsContainer = $("<div>").addClass('months-container');
			this.error = $("<div>").addClass('error').html("Please choose the start/end time for the days you've selected");
			this.closeButton = $("<div>").addClass('close-button').html("Close");
			this.resetButton = $("<div>").addClass('reset-button').html("Clear");
			$(this.element).after(this.deck);
			$(this.deck).append(this.error).append(this.monthsContainer).append(this.resetButton).append(this.closeButton);
			this.addMonth(date.getFullYear(), date.getMonth() + 1);
			$(this.element).on("click", function() {
				setTimeout(function() {
					$(that.deck).show();
				}, 100);
			});
			$(this.closeButton).on("click", function() {
				var valid = that.validate();
				if(valid) {
					$(that.deck).hide();
					$(that.error).hide();
					$(that.element).val(that.getText());
					$("#id_description").data("description").setDays(that.getDays());
				} else {
					$(that.error).show();
				}

			});
			$(this.resetButton).on("click", function() {
				var agree = confirm("Are you sure you want to clear form?")
				if(agree) that.clear();
			});			
		},
		setValue: function(years){			
			this.clear();
			for(yi in years) if(years.hasOwnProperty(yi)){
				var months = years[yi];
				for(mi in months) if(months.hasOwnProperty(mi)){
					var days = months[mi];
					this.addMonth(yi, mi);
					for(di in days) if(days.hasOwnProperty(di)){
						var start = days[di].start,
							end = days[di].end,
							daysTimePicker = this.months[yi][mi];						
						daysTimePicker.addDay(parseInt(di), parseInt(mi), parseInt(yi));
						var format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(yi, mi-1, di));
						$(".days-picker", $(daysTimePicker.element).parents(".months-container")).multiDatesPicker('addDates', format_day);
						//$(".days-time-picker", $(this).parents(".month-container")).data("daystimepicker").addDay(that.options.day, that.options.month, that.options.year);
						timePicker = _.filter(daysTimePicker.days, function(day){
							return day.options.day == di;
						})[0];
						timePicker.startTime.val(start);
						timePicker.endTime.val(end);
					}
				}
			}

		},
		addMonth: function(year, month) {
			if((year in this.months) && (month in this.months[year])){
				return;
			}
			var monthContainer, days;
			date = new Date();
			year && date.setFullYear(year);
			month && date.setMonth(month - 1);
			$(this.monthsContainer).append(monthContainer = this.monthContainer(date));
			days = $(".days-time-picker", monthContainer).data("daystimepicker");
			if(!(year in this.months)) this.months[year] = {};
			this.months[year][month] = days;
		},
		monthPicker: function(month_from, month_to) {
			return $("<div>").addClass("month-picker");
		},
		monthContainer: function(date) {
			var that = this,
				widget, daysTimePicker, monthPicker, daysPicker, monthAndDaysWrapper, now = (new Date());
			daysPicker = $("<div>").addClass("days-picker").multiDatesPicker({
				onSelect: function(dateText, inst) {
					var timepicker = $(daysTimePicker).data("daystimepicker");
					timepicker.addDay(inst.currentDay, inst.currentMonth, inst.currentYear);
					if(timepicker.days.length === 0) {
						$(timepicker.labels).removeClass("active");
					} else {
						$(timepicker.labels).addClass("active");
					}
				},
				onChangeMonthYear: function() {
					if(daysTimePicker) {
						timepicker = $(daysTimePicker).data("daystimepicker");
						timepicker.clear();
						$(this).multiDatesPicker('resetDates');
						$(timepicker.labels).removeClass("active");
					}
				},
				beforeShowDay: function(date) {
					return [date >= now];
				},

			}).datepicker("setDate", date);
			monthPicker = this.monthPicker();


			monthAndDaysWrapper = $("<div>").addClass("month-and-days-wrapper").
			append(daysPicker).
			append(monthPicker);

			monthPicker.newMonthPicker();

			$(monthPicker).on("monthselected", function(event, year, month) {
				that.addMonth(year, month);
			});
			daysTimePicker = $("<div>").addClass("days-time-picker").daystimepicker();
			widget = $("<div>").addClass("month-container").append(monthAndDaysWrapper).append(daysTimePicker);

			var disabledOrEnableMonths = function(year) {
					if((year || date.getFullYear()) == (new Date()).getFullYear()) {
						var allMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
							disabledMonths;
						disabledMonths = allMonths.filter(function(month) {
							return month < (new Date().getMonth() + 1);
						});
						$($(monthPicker).data("newMonthPicker").monthValue).monthpicker('disableMonths', disabledMonths);

					} else {
						$($(monthPicker).data("newMonthPicker").monthValue).monthpicker('disableMonths', []);
					}
				}
			setTimeout(disabledOrEnableMonths, 100);
			$($(monthPicker).data("newMonthPicker").monthValue).monthpicker().bind("monthpicker-change-year", function(e, year) {
				disabledOrEnableMonths(year);
			});
			return widget;
		},
		getText: function() {
			var days = this.getDays(),
				minDay, maxDay;
			if(days.length === 0) return '';
			minDay = Math.min.apply(null, days);
			maxDay = Math.max.apply(null, days);
			if(minDay === maxDay) {
				return $.datepicker.formatDate('dd-M-yy', new Date(minDay));
			} else {
				return $.datepicker.formatDate('dd-M-yy', new Date(minDay)) + ' to ' + $.datepicker.formatDate('dd-M-yy', new Date(maxDay));
			}

		},
		getJson: function() {
			var value = {};
			for(var yi in this.months) if(this.months.hasOwnProperty(yi)) {
				var months = this.months[yi];
				value[yi] = {};
				for(var mi in months) if(months.hasOwnProperty(mi)) {
					var days = months[mi].days;
					value[yi][mi] = {}
					for(var di in days) if(days.hasOwnProperty(di)) {
						var times = days[di];
						value[yi][mi][times.options.day] = {
							start: $(times.startTime).val(),
							end: $(times.endTime).val(),
						}
					}
				}
			}
			console.log(value);
			$("#id_when_json").val(JSON.stringify(value));
			return value;
		},
		getDays: function() {
			var json = this.getJson(),
				result = [];
			for(var year in json) if(json.hasOwnProperty(year)) {
				months = json[year];
				for(var month in months) if(months.hasOwnProperty(month)) {
					days = months[month];
					for(var day in days) if(days.hasOwnProperty(day)) {
						result.push(new Date(year, month - 1, day));
					}
				}
			}
			return result;
		},
		validate: function() {
			var json = this.getJson(),
				valid = true;
			for(var year in json) if(json.hasOwnProperty(year)) {
				months = json[year];
				for(var month in months) if(months.hasOwnProperty(month)) {
					days = months[month];
					for(var day in days) if(days.hasOwnProperty(day)) {
						if(!days[day].start || !days[day].end) return false;
					}
				}
			}
			return true;
		},
		clear: function() {
			$(this.deck).remove();
			this.months = {};
			this._initDeck();
		}

	});

	$.widget("ui.newMonthPicker", {
		_create: function() {
			var that = this;
			id = "mp_" + (+Date.now());
			this.monthValue = $("<input>").addClass("hidden monthpicker").attr("data-month-id", id);
			this.selectWrapper = $("<div>").addClass("wrapper");
			this.label = $("<span>").html("Select More Months");
			this.selectButton = $("<div>").addClass("new-month-select-arrow");
			$(this.selectWrapper).append(this.label).append(this.selectButton);
			$(this.element).
			append(this.monthValue).
			append(this.selectWrapper);

			if(date.getMonth() == 11) {
				date.setFullYear(date.getFullYear() + 1)
				date.setMonth(0);
			} else {
				date.setMonth(date.getMonth() + 1)
			}

			$(this.monthValue).monthpicker({
				openOnFocus: false,
				id: id,
				startYear: date.getFullYear(),
				finalYear: date.getFullYear() + 5
			});

			$(this.selectWrapper).on("click", function() {
				$(that.monthValue).monthpicker('show');
			});

			$(this.monthValue).monthpicker().bind('monthpicker-click-month', function(e, month) {
				var monthpicker = $(this).data("monthpicker"),
					year;
				year = monthpicker.settings.selectedYear;
				// bug in monthpicker
				if(monthpicker.settings.startYear > monthpicker.settings.selectedYear) {
					year = monthpicker.settings.startYear
				}
				$(that.element).trigger("monthselected", [year, month]);

			});
		}
	});

	$.widget("ui.daystimepicker", {
		_create: function() {
			this.days = [];
			this._initDeck();
		},
		_initDeck: function() {
			this.labels = $("<div>").addClass("dtp-labels");
			this.labels.append($("<p>").html("Start Time"));
			this.labels.append($("<p>").html("End Time"));
			this.labels.append($("<p>").html("Auto fill"));
			this.daysContainer = $("<div>").addClass("days-container");
			$(this.element).append(this.labels).append(this.daysContainer);
		},
		clear: function() {
			for(var i in this.days) if(this.days.hasOwnProperty(i)) {
				$(this.days[i].element).remove();
			}
			this.days = [];
		},
		addDay: function(day, month, year) {
			var index
			if((index = this.days.map(function(day) {
				return day.options.day
			}).indexOf(day)) !== -1) {
				$(this.days.splice(index, 1)[0].element).remove();
				return;
			}
			var previous = this.findPrevious(day),
				timePicker = this.timePicker(day, month, year);
			if(this.days.length === 0) {
				this.days = [];
			}
			if(previous) {
				this.days.splice(
				this.days.indexOf(previous) + 1, 0, $(timePicker).data("timepicker"));
				$(previous.element).after(timePicker)
			} else {
				this.days.splice(
				0, 0, $(timePicker).data("timepicker"));
				$(this.daysContainer).prepend(timePicker);
			}
			if(this.days.length === 0) {
				$(this.labels).removeClass("active");
			} else {
				$(this.labels).addClass("active");
			}
		},
		findPrevious: function(day) {
			if(this.days.length) {
				var maxDay, tempDay;
				for(var di in this.days) {
					tempDay = this.days[di];
					if(tempDay.options.day < day) {
						maxDay = tempDay;
					} else {
						return maxDay || false;
					}
				}
				return maxDay;
			} else {
				return false;
			}
		},
		findNext: function(day) {
			if(this.days.length) {
				var minDay = false,
					tempDay;
				for(var di in this.days) {
					tempDay = this.days[di];
					if(tempDay.options.day > day) {
						minDay = tempDay;
						return minDay
					}
				}
				return minDay;
			} else {
				return false;
			}
		},
		timePicker: function(day, month, year) {
			return $("<div>").addClass("my-time-picker").timepicker({
				day: day,
				month: month,
				year: year,
				container: this
			});
		}
	});

	$.widget("ui.timepicker", {
		options: {
			day: null,
			container: null
		},
		_create: function() {
			var that = this;
			this.label = $("<div>").addClass("day-value").html(this.options.day);
			this.startTime = $("<input>").addClass("start-time");
			this.endTime = $("<input>").addClass("end-time");
			this.autoFill = $("<div>").addClass("checkbox autofill");
			this.removeButton = $("<div>").addClass("remove");
			this.daystimeContainer = this.options.container;
			$(this.element).
			append(this.label).
			append(this.startTime).
			append(this.endTime).
			append(this.autoFill).
			append(this.removeButton);

			function changeNext() {
				if(that.next()) {
					if(that.next().isAutoFill()) {
						that.next().setValue(
						that.getValue());
					}
					that.next().changeNext()
				}
			};

			this.startTime.ptTimeSelect({
				onClose: changeNext
			});
			this.endTime.ptTimeSelect({
				onClose: changeNext
			});

			$(this.removeButton).on('click', function() {
				var format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(that.options.year, that.options.month, that.options.day));
				$(".days-picker", $(this).parents(".month-container")).multiDatesPicker('removeDates', format_day);
				$(".days-time-picker", $(this).parents(".month-container")).data("daystimepicker").addDay(that.options.day, that.options.month, that.options.year);				
			})

			// oldTime =  $.timePicker(this.startTime).getTime();
			// $(this.startTime).on("change", function(){
			// 	if(that.endTime.val()){
			// 		var duration = ($.timepicker(that.endTime).getTime()-oldTime),
			//  					time = $.timePicker(that.startTime.getTime());
			//  					// Calculate and update the time in the second input.
			//  				$.timePicker(that.endTime).setTime(new Date(new Date(time.getTime() + duration)));
			//  				oldTime = time;
			// 	}
			// });
			// $(this.endTime).on("change", function() {
			// 			if($.timePicker(this.startTime).getTime() > $.timePicker(this).getTime()) {
			//  				$(this).addClass("error");
			// 			}
			// 			else {
			//  				$(this).removeClass("error");
			// 			}
			// });
			$(this.autoFill).on("click", function() {
				$(this).toggleClass("checked");
				if($(this).hasClass("checked")) {
					that.setValue(
					that.previous().getValue());
				}
			});
		},
		changeNext: function() {
			if(this.next()) {
				if(this.next().isAutoFill()) {
					this.next().setValue(
					this.getValue());
				}
				this.next().changeNext()
			}
		},
		isAutoFill: function() {
			return $(this.autoFill).hasClass("checked")
		},
		previous: function() {
			return this.daystimeContainer.findPrevious(this.options.day);
		},
		next: function() {
			return this.daystimeContainer.findNext(this.options.day);
		},
		getValue: function() {
			return {
				startTime: $(this.startTime).val(),
				endTime: $(this.endTime).val()
			}
		},
		setValue: function(value) {
			$(this.startTime).val(value.startTime);
			$(this.endTime).val(value.endTime);
		}
	});

	$(document).ready(function() {
		$("#id_when").when();		
		if($("#id_when_json").val()){
			$("#id_when").data("when").setValue(
				JSON.parse(
					$("#id_when_json").val()
				)
			);			
		};
	});

})(jQuery);