(function($) {
	// For IE8 and earlier version.
	if(!Date.now) {
		Date.now = function() {
			return new Date().valueOf();
		}
	}
	if(!Array.prototype.indexOf) {
		Array.prototype.indexOf = function(obj, start) {
			for(var i = (start || 0), j = this.length; i < j; i++) {
				if(this[i] === obj) {
					return i;
				}
			}
			return -1;
		}
	}

	$.widget("ui.when", {
		_create: function() {
			this.months = {
				//	2012: { 10: }
			};
			this._initDeck();
		},
		_initDeck: function() {
			var that = this,
				date = new Date(),
				disabledOrEnableMonths;

			this.deck = $("<div>").addClass('ui-widget when-deck');
			this.monthsContainer = $("<div>").addClass('months-container');
			this.error = $("<div>").addClass('error').html("Please choose the start/end time for the days you've selected");
			this.multiSelectModeSpan = $("<span>");
			this.multiSelectModeSpan.html("Use Shift Key to select more than one day");
			this.sumbitButton = $("<div>").addClass('submit-button').html("Submit");
			this.resetButton = $("<div>").addClass('reset-button').html("Clear");
			this.cancelButton = $("<div>").addClass('cancel-button').html("Cancel");
			this.monthPicker = $("<div>").addClass("month-picker");

			$(this.element).after(this.deck);
			$(this.deck).append(this.error).
			append(this.multiSelectModeSpan).
			append(this.monthsContainer).
			append(this.monthPicker).
			append(this.resetButton).
			append(this.cancelButton).
			append(this.sumbitButton);

			this.monthPicker.newMonthPicker();

			$(this.monthPicker).on("monthselected", function(event, year, month) {
				that.addMonth(year, month);
			});

			disabledOrEnableMonths = function(year) {
				//TODO: disable month in used
				if((year || date.getFullYear()) == (new Date()).getFullYear()) {
					var allMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
						disabledMonths;
					disabledMonths = _.filter(allMonths, function(month) {
						return month < (new Date().getMonth() + 1);
					});
					$($(that.monthPicker).data("newMonthPicker").monthValue).monthpicker('disableMonths', disabledMonths);

				} else {
					$($(that.monthPicker).data("newMonthPicker").monthValue).monthpicker('disableMonths', []);
				}
			}
			setTimeout(disabledOrEnableMonths, 100);

			$($(this.monthPicker).data("newMonthPicker").monthValue).monthpicker().bind("monthpicker-change-year", function(e, year) {
				disabledOrEnableMonths(year);
			});

			this.addMonth(date.getFullYear(), date.getMonth() + 1);
			$(this.element).on("click", function() {
				setTimeout(function() {
					$.fancybox($(that.deck), {
						autoSize: true,
						closeBtn: true,
						hideOnOverlayClick: false
					});
				}, 100);
			});
			$(this.sumbitButton).on("click", function() {
				var valid = that.validate();
				if(valid) {
					$.fancybox.close();
					$(that.error).hide();
					$(that.element).val(that.getText());
					$("#id_description").data("description").setDays(that.getDays());
				} else {
					$(that.error).show();
				}
			});
			$(this.cancelButton).on("click", function() {
				$.fancybox.close();
				$(that.error).hide();
			});
			$(this.resetButton).on("click", function() {
				var agree = confirm("Are you sure you want to clear form?")
				if(agree) {
					that.clear();
					//$.fancybox.close();
				}
			});
		},
		setValue: function(years) {
			this.clear();
			for(yi in years) if(years.hasOwnProperty(yi)) {
				var months = years[yi];
				for(mi in months) if(months.hasOwnProperty(mi)) {
					var days = months[mi];
					this.addMonth(yi, mi);
					for(di in days) if(days.hasOwnProperty(di)) {
						var start = days[di].start,
							end = days[di].end,
							daysTimePicker = this.months[yi][mi];
						daysTimePicker.addDay(parseInt(di), parseInt(mi), parseInt(yi));
						var format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(yi, mi - 1, di));
						$(".days-picker", $(daysTimePicker.element).parents(".months-container")).multiDatesPicker('addDates', format_day);
						//$(".days-time-picker", $(this).parents(".month-container")).data("daystimepicker").addDay(that.options.day, that.options.month, that.options.year);
						timePicker = _.filter(daysTimePicker.days, function(day) {
							return day.options.day == di;
						})[0];
						timePicker.startTime.val(start);
						timePicker.endTime.val(end);
					}
				}
			}

		},
		addMonth: function(year, month) {
			// TODO: insert month beetween it neighb...
			if((year in this.months) && (month in this.months[year])) {
				return;
			}
			var monthContainer, days;
			date = new Date();
			year && date.setFullYear(year);
			month && date.setMonth(month - 1);
			date.setDate(1);
			prevDaysTimePicker = this.findPrevDaysTimePicker(year, month);
			monthContainer = this.monthContainer(date, year, month);
			if(prevDaysTimePicker) {
				$(prevDaysTimePicker).after(monthContainer);
			} else {
				$(this.monthsContainer).prepend(monthContainer);
			}

			days = $(".days-time-picker", monthContainer).data("daystimepicker");
			if(!(year in this.months)) this.months[year] = {};
			this.months[year][month] = days;
		},
		removeMonth: function(year, month) {
			delete this.months[year][month];
			if(this.months[year].length == 0) {
				delete this.months[year];
			}
		},
		findPrevDaysTimePicker: function(year, month) {
			var element;
			$(".month-container .days-picker").each(function() {
				if((year > this.year) || ((year == this.year) && (month > this.month))) {
					element = $(this).parents(".month-container")[0];
				}
			});
			return element;
		},
		monthContainer: function(date, year, month) {
			var that = this,
				widget, daysTimePicker, multiSelectModeWrapper, removeButton, daysPicker, monthAndDaysWrapper, now = (new Date());

			multiSelectModeWrapper = $("<div>").addClass("multi-select-mode-wrapper");

			removeButton = $("<span>").addClass("remove");

			multiSelectModeWrapper.append(removeButton);

			daysPicker = $("<div>").addClass("days-picker").multiDatesPicker({
				onToggle: function(dateText) {
					var timepicker = $(daysTimePicker).data("daystimepicker");
					var dateArray = dateText.split("/");
					var month = dateArray[0];
					var day = dateArray[1];
					var year = dateArray[2];
					timepicker.addDay(day, month, year);
					if(timepicker.days.length === 0) {
						$(timepicker.labels).removeClass("active");
						$(timepicker.labels).parents(".month-container").removeClass("hidden-arrows");
					} else {
						$(timepicker.labels).addClass("active");
						$(timepicker.labels).parents(".month-container").addClass("hidden-arrows");
					}
				},
				onChangeMonthYear: function(year, month) {
					that.removeMonth(this.year, this.month);
					if((year in that.months) && (month in that.months[year])) {
						year = this.year;
						month = this.month;
					}
					$(this).parents(".month-container").remove();
					that.addMonth(year, month);
				},
				beforeShowDay: function(date) {
					return [date >= now];
				},
				mode: 'normal',
				defaultDate: date
			});
			daysPicker[0].year = year;
			daysPicker[0].month = month;
			/*multiSelectMode.on("change", function(){
				if(this.checked){
					daysPicker.multiDatesPicker("setMode", { mode:"range" });
				} else {
					daysPicker.multiDatesPicker("setMode", { mode:"normal"});
				}
			});*/

			removeButton.on("click", function() {
				if($(".month-container").length === 1) {
					alert("You can not remove this month");
					return;
				}
				if(confirm("Do you realy want to remove this month?")) {
					that.removeMonth(daysPicker[0].year, daysPicker[0].month);
					$(this).parents(".month-container").remove();
				}
			})

			monthAndDaysWrapper = $("<div>").addClass("month-and-days-wrapper").
			append(multiSelectModeWrapper).
			append(daysPicker);

			daysTimePicker = $("<div>").addClass("days-time-picker").daystimepicker();
			widget = $("<div>").addClass("month-container").append(monthAndDaysWrapper).append(daysTimePicker);
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
			$.fancybox($(this.deck), {
				autoSize: true,
				closeBtn: true,
				hideOnOverlayClick: false
			});
		}

	});

	$.widget("ui.newMonthPicker", {
		_create: function() {
			var that = this,
				date;
			date = new Date();
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
			if((index = _.map(this.days, function(day) {
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
				$(this.labels).parents(".month-container").removeClass("hidden-arrows");
			} else {
				$(this.labels).addClass("active");
				$(this.labels).parents(".month-container").addClass("hidden-arrows");
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
				if(confirm("Do you realy want to remove day?")) {
					var format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(that.options.year, that.options.month - 1, that.options.day));
					$(".days-picker", $(this).parents(".month-container")).multiDatesPicker('toggleDate', format_day);
					//$(".days-time-picker", $(this).parents(".month-container")).data("daystimepicker").addDay(that.options.day, that.options.month, that.options.year);					
				}
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
		$('[data-event="click"] a').live("mousemove", function(e) {
			if(!('event' in window)) {
				window.eventObj = e;
			}
		});
		$("#id_when").when();
		if($("#id_when_json").val()) {
			$("#id_when").data("when").setValue(
			JSON.parse(
			$("#id_when_json").val()));
		};
	});

})(jQuery);