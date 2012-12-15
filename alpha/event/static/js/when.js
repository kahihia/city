(function($){
	$.widget("ui.when", {
		_create : function(){
			this._initDeck();
		},
		_initDeck : function(){
			var that = this;
			this.deck = $("<div>").addClass('ui-widget when-deck');
			this.monthsContainer = $("<div>").addClass('months-container');
			this.closeButton = $("<div>").addClass('close-button').html("Close");
			$(this.element).after(this.deck);
			$(this.deck).append(this.monthsContainer).
									 append(this.closeButton);
			this._initMonthsContainer();
			$(this.element).on("click", function(){
				setTimeout(function(){
					$(that.deck).show();
				},100);
			});
			$(this.closeButton).on("click", function(){
				$(that.deck).hide();
			})
		},
		_initMonthsContainer : function(){
			$(this.monthsContainer).append(this.monthContainer(new Date().getMonth()));
		},
		monthPicker : function(month_from, month_to){
			return $("<div>").addClass("month-picker");
		},
		monthContainer : function(month) {
			var that=this,
				daysTimePicker, monthPicker, daysPicker, monthAndDaysWrapper;
			daysPicker = $("<div>").addClass("days-picker").multiDatesPicker({
				onSelect: function(dateText, inst){
					console.log([dateText, inst]);
					// Here to start
					$(daysTimePicker).data("daystimepicker").addDay(inst.currentDay);
				}
			});
			monthPicker = this.monthPicker();
			monthAndDaysWrapper = $("<div>").addClass("month-and-days-wrapper").
				append(daysPicker).
				append(monthPicker);

			monthPicker.newMonthPicker();
			daysTimePicker = $("<div>").addClass("days-time-picker").daystimepicker();
			return $("<div>").addClass("month-container")
						.append(monthAndDaysWrapper)
						.append(daysTimePicker);
		},
		addMonth : function(month){
			this.monthWidgets.push(new MonthWidget(month));
			this.selectMonthWidgets.push(new SelectMonthWidget());
		},
		drawTo : function(place){
			var monthWidget, selectMonthWidget;
			this.container = place;
			for(var mi in this.monthWidgets) if(this.monthWidgets.hasOwnProperty(mi)) {
				monthWidget = this.monthWidgets[mi];
				selectMonthWidget = this.selectMonthWidgets[mi];
				monthWidget.drawTo(this.prepareContainer());
				selectMonthWidget.drawTo(this.prepareContainer());
			}
		}
	});

	$.widget("ui.newMonthPicker", {
		_create: function(){
			var that = this;
					id ="mp_" + (+Date.now());
			this.monthValue = $("<input>").addClass("hidden monthpicker").attr("data-month-id", id);

			this.label = $("<span>").html("Select month");
			this.selectButton = $("<div>").addClass("new-month-select-arrow");
			$(this.element).
				append(this.monthValue).
				append(this.label).
				append(this.selectButton);

			$(this.monthValue).monthpicker({
				openOnFocus: false,
				id: id
			});

			$(this.selectButton).on("click", function(){
				$(that.monthValue).monthpicker('show');
			});
		}
	});

	$.widget("ui.daystimepicker", {
		_create: function(){
			this.days = [];
			this._initDeck();
		},
		_initDeck: function(){
			this.labels = $("<div>").addClass("dtp-labels");
			this.labels.append($("<p>").html("Start Time"));
			this.labels.append($("<p>").html("End Time"));
			this.labels.append($("<p>").html("Auto fill"));
			this.daysContainer = $("<div>").addClass("days-container");
			$(this.element).append(this.labels).append(this.daysContainer);
		},
		addDay: function(day){
			var previous = this.findPrevious(day),
				timePicker = this.timePicker({
					day: day,
					daystimeContainer: this
				});
			if(this.days.length===0){
				this.days = [];
			}
			if(previous){
				this.days.splice(
					this.days.indexOf(previous)+1, 0, $(timePicker).data("timepicker")
				);
				$(previous.element).after(timePicker)
			} else {
				this.days.splice(
					0, 0, $(timePicker).data("timepicker")
				);
				$(this.daysContainer).prepend(timePicker);
			}
		},
		findPrevious: function(day){
			if(this.days.length){
				var maxDay, tempDay;
				for(var di in this.days){
					tempDay = this.days[di];
					if(tempDay.options.day.day<day){
						maxDay = tempDay;
					} else {
						return maxDay||false;
					}
				}
				return maxDay;
			} else {
				return false;
			}
		},
		findNext: function(day){
			if(this.days.length){
				var minDay=false, tempDay;
				for(var di in this.days){
					tempDay = this.days[di];
					if(tempDay.options.day.day>day){
						minDay = tempDay;
						return minDay
					}
				}
				return minDay;
			} else {
				return false;
			}
		},
		timePicker: function(day){
			return $("<div>").addClass("my-time-picker").timepicker({
				day:day,
				container: this
			});
		}
	});

	$.widget("ui.timepicker", {
		options : {
			day:null,
			container: null
		},
		_create: function(){
			var that = this;
			this.label = $("<div>").addClass("day-value").html(this.options.day.day);
			this.startTime = $("<input>").addClass("start-time");
			this.endTime = $("<input>").addClass("end-time");
			this.autoFill = $("<div>").addClass("checkbox autofill");
			this.daystimeContainer = this.options.container;
			$(this.element).
				append(this.label).
				append(this.startTime).
				append(this.endTime).
				append(this.autoFill);

			function changeNext(){
				if(that.next()){
					if(that.next().isAutoFill()){
						that.next().setValue(
							that.getValue()
						);
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

			$(this.autoFill).on("click", function(){
				$(this).toggleClass("checked");
				if($(this).hasClass("checked")){
					that.setValue(
						that.previous().getValue()
					);
				}
			});
		},
		changeNext: function(){
			if(this.next()){
				if(this.next().isAutoFill()){
					this.next().setValue(
						this.getValue()
					);
				}
				this.next().changeNext()
			}
		},
		isAutoFill: function(){
			return $(this.autoFill).hasClass("checked")
		},
		previous : function(){
			return this.daystimeContainer.findPrevious(this.options.day.day);
		},
		next : function(){
			return this.daystimeContainer.findNext(this.options.day.day);
		},
		getValue: function(){
			return {
				startTime : $(this.startTime).val(),
				endTime : $(this.endTime).val()
			}
		},
		setValue: function(value){
			$(this.startTime).val(value.startTime);
			$(this.endTime).val(value.endTime);
		}
	});

	$(document).ready(function(){
		$("#id_when").when();
	});

})(jQuery);