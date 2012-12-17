(function($) {
   function PopupManager() {
     var that = this;
     this.current = null;
     
     $(document).bind(
       'click',
       function(e) {
	 that.hideCurrent();
       });
   }

   PopupManager.prototype.hideCurrent = function() {
     if (this.current) {
       this.current.hide();
       this.current = null;
     }
   };

   PopupManager.prototype.show = function(elem) {
     if (this.current == elem) { return; }
     this.hideCurrent();
     this.current = elem;
     elem.show();
   };

   PopupManager.prototype.isShowing = function(elem) {
     return this.current == elem;
   };

   $.popupManager = new PopupManager();

   var month_names = ['January', 'February', 'March', 'April', 'May',
		      'June', 'July', 'August', 'September', 'October',
		      'November', 'December'];

   function createHead(options) {
     var month_name = month_names[options.startOfMonth.month];
     var year = options.startOfMonth.year;
     var content = (
	 '<div class="newcal-header">' +
	 '<div class="newcal-month-left">&laquo;</div>' +
	 '<div class="newcal-month-right">&raquo;</div>' +
	 '<div class="newcal-month" colspan="5">' + month_name + ' ' + year + '</div>' +
	 '</div>');
     return $(content);
   }

   function createTable(options) {
     var table = $('<table class="newcal-table"/>');     
     return table;
   }

   function createDays() {
     var days = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
     var html = ['<tr>'];
     for (var i in days) {
       if (days.hasOwnProperty(i)) {
	 html.push('<td class="newcal-day-head">' + days[i] + '</td>');
       }
     }
     html.push('</tr>');
     return $( html.join("") );
   }

   function startOfMonth(date) {
     date = date || new Date();
     date = new Date(date.getFullYear(), date.getMonth(), 1);
     var start = { 'day' : date.getDay(),
		   'month' : date.getMonth(),
		   'year' : date.getFullYear() };
     return start;
   }
   window.sotm = startOfMonth;

   function createCalendarArrayRows(start) {
     var rows = [], current = [], i;
     rows.push(current);
     var now = new Date(start.year, start.month, 1);
     
     // insert blank entries to start off the month
     for(i=0; i < start.day; i++) {
       current.push('');
     }

     // fill the rest
     while (now.getMonth() === start.month) {
       if (current.length == 7) {
	 current = [];
	 rows.push(current);
       }
       current.push(now.getDate());
       now = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
     }
     while (current.length < 7) {
       current.push('');
     }
     return rows;
   }
   window.ccar = createCalendarArrayRows;

   function createCalendarRow(options, row) {
     var i, elem, entries = $(), cell, today = new Date();
     today = new Date(today.getFullYear(), today.getMonth(), today.getDate());
     for (i in row) {
       if (row.hasOwnProperty(i)) {
	 elem = row[i];
	 if (elem === '') {
	   entries = entries.add( $('<td class="newcal-noday"></td>'));
	 } else {
	   var date = new Date(options.startOfMonth.year,
			       options.startOfMonth.month,
			       elem);
	   cell = $('<td class="newcal-day">' + elem + '</td>')
	     .bind(
	       'click',
	       (function(day, date) {
		 return function(e) { 
		   if (options['onClick']) {
		     options.onClick(date, options.element);
		   }
		   $.popupManager.hideCurrent();
		 };
		}(elem, date)));
	   if ( (today.getFullYear() === options.startOfMonth.year) &&
	     (today.getMonth() === options.startOfMonth.month) &&
		(today.getDate() == elem)) {
	     cell.addClass("newcal-today");
	   }
	   if (date < today) {
	     cell.addClass("newcal-past");
	   }
	   entries = entries.add( cell );
	 }
       }
     }
     return entries;
   }

   function createCalendarRows(options, rows) {
     var i, row, html = [];
     var outrows = $();
     for (i in rows) {
       if (rows.hasOwnProperty(i)) {
	 row = $('<tr>');
	 row.append(createCalendarRow(options, rows[i]));
	 outrows = outrows.add(row);
       }
     }
     return outrows;
   }
   
   function populateDiv(options, div) {
     div.append(createHead(options));
     var table = createTable(options)
       .append(createDays(options))
       .append(createCalendarRows(options, createCalendarArrayRows(options.startOfMonth)));
     div.append(table);
   };

   function make_month_nav_handler(delta, div, options) {
     return (function() {
       var new_month = startOfMonth(
	 new Date(options.startOfMonth.year, 
		  options.startOfMonth.month + delta, 
		  1));
       var new_options = $.extend(true, {}, options);
       new_options.startOfMonth = new_month;
       div.newcal_fill(new_options);
     });
          
   }

   $.fn.newcal_fill = function(options) {
     options = options || {};
     options.startOfMonth = options.startOfMonth || startOfMonth();
     return this.each(
       function() {
	 var div = $(this);
	 div.children().remove();
	 populateDiv(options, div);
	 div.find('.newcal-month-left').bind(
	   'click', make_month_nav_handler(-1, div, options));
	 div.find('.newcal-month-right').bind(
	   'click', make_month_nav_handler(1, div, options));
       });
   };

   /***
    * Options for newcal:
    *   onClick: function(date) - function to call when a date is selected
    */
   $.fn.newcal = function(options) {
     options = options || {};
     options.startOfMonth = startOfMonth();
     return this.each(
       function() {
	 var this_options = jQuery.extend(true, {}, options);
	 var context = { div: null };
	 var element = $(this);
	 this_options.element = element;
	 element.bind(
	   'click',
	   function(e) {
	     if (context.div) { 
	       if (options.toggles && $.popupManager.isShowing(context.div)) {
		 $.popupManager.hideCurrent();
		 return false;
	       }
	       $.popupManager.show(context.div); 
	       return false; 
	     }
	     var offset = element.position();
	     var padding = element.css('padding-left');
	     context.div = $('<div />')
	       .addClass('newcal-date-popup')
	       .css(
		 { position: 'absolute',
		   left: offset.left + parseInt(element.css('marginLeft')),
		   top: offset.top + element.outerHeight()
		 })
	       .bind('click', function(e) { e.stopPropagation(); e.preventDefault(); return false; });
	     element.after(context.div);
	     e.preventDefault();
	     context.div.newcal_fill(this_options);
	     $.popupManager.show(context.div);
	     return false;
	   });
       });
   };

   $.newcal_input_callback = function(date, elem) {
     var formatted = sprintf("%04d-%02d-%02d",
			    date.getFullYear(), date.getMonth()+1,
			    date.getDate());
     elem.val(formatted);
   };
   
   function jumpToDate(date) {
     window.location = sprintf("/events/all/%04d-%02d-%02d", date.getFullYear(),
			       date.getMonth() + 1, date.getDate());
   }
   window.jumpToDate = jumpToDate;

   function highlight_correct_elements(ctx) {
     var div = ctx.state.div;
     div.find(".newtime-active").removeClass('newtime-active');
     div.find(".newtime-hours li").each(
       function() {
	 var e = $(this);
	 if (e.text() == ctx.state.hour) {
	   e.addClass('newtime-active');
	 }
       });
     div.find(".newtime-minutes li").each(
       function() {
	 var e = $(this);
	 if (e.text() == sprintf("%02d", ctx.state.minute)) {
	   e.addClass('newtime-active');
	 }
       });
     div.find(".newtime-period li").each(
       function() {
	 var e = $(this);
	 if (e.text() == ctx.state.period) {
	   e.addClass('newtime-active');
	 }
       });
   }

   function make_list(elements, classes, clickhandler) {
     var main_tag, main_elem, inner_tag;
     if (classes) {
       main_tag = '<ul class="' + classes + '"/>';
     } else {
       main_tag = '<ul/>';
     }
     main_elem = $(main_tag);
     for (var i in elements) {
       if (elements.hasOwnProperty(i)) {
	 inner_tag = $('<li/>').html(elements[i])
	   .bind('click',
		function(e) { 
		  if (clickhandler) {
		    clickhandler(this); 
		  }
		});
	 main_elem.append( inner_tag );
       }
     }
     return main_elem;
   };

   function make_header(text) {
     return $("<div>").addClass("newtime-header").html(text);
   }

   function NewtimeContext(initial) {
     var defaults = {
       hour: 12,
       minute: 0,
       period: 'AM',
       container: null,
       refreshCallback: null
     };
     this.state = jQuery.extend(true, {}, defaults, initial);
   };

   NewtimeContext.prototype.setHour = function( hour ) {
     this.state.hour = parseInt(hour, 10);
     this.refresh();
   };
   NewtimeContext.prototype.setMinute = function( minute ) {
     this.state.minute = parseInt(minute, 10);
     this.refresh();
   };
   NewtimeContext.prototype.setPeriod = function( period ) {
     this.state.period = period;
     this.refresh();
   };
   NewtimeContext.prototype.setTimeFromString = function( timeString ) {
     // assume it follows a normal pattern
     var re = /(\d+):(\d+) ?(\w+)/;
     var match = re.exec(timeString);
     if (match && match.length == 4) {
       this.state.hour = parseInt(match[1], 10);
       this.state.minute = parseInt(match[2], 10);
       this.state.period = match[3];
       this.refresh();
     }
   };

   NewtimeContext.prototype.refresh = function() {
     var timestring = sprintf("%d:%02d %s", this.state.hour, this.state.minute,
			this.state.period);
     this.state.container.find(".newtime-header").html(timestring);
     if (this.state.refreshCallback) {
       this.state.refreshCallback(timestring);
     }
   };

   $.newtime_create = function(options, ctx) {
     hours = [ 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
     minutes = [ '00', '05', 10, 15, 20, 25, 30, 35, 40, 45, 50, 55 ];
     periods = [ 'AM', 'PM' ];
     var elem = ctx.state.div;

     //  elem.children().remove();
     //	 elem.append( make_header("header here"));
     elem.append( make_list(hours, "newtime-hours",
			    function(e) {
			      ctx.setHour($(e).text());
			      highlight_correct_elements(ctx);
			    }));
     elem.append( make_list(minutes, "newtime-minutes",
			    function(e) {
			      ctx.setMinute($(e).text());
			      highlight_correct_elements(ctx);
			    }));
     elem.append( make_list(periods, "newtime-period",
			    function(e) {
			      ctx.setPeriod($(e).text());
			      highlight_correct_elements(ctx);
			    }));
   };

   $.fn.newtime = function(options) {
     options = options || {};
     // bind to input fields
     return this.each(
       function() {
	 var element = $(this);
	 var context = new NewtimeContext(
	   { container: element, 
	     div: null,
	     refreshCallback: function(s) {
	       element.val(s);
	       highlight_correct_elements(context);
	     }
	   });
	 element.bind(
	   'focus click', 
	   function(e) {
	     if (context.state.div) { 
	       context.setTimeFromString( element.val() );
	       $.popupManager.show(context.state.div); 
	       return false; 
	     }
	     var offset = element.position();
	     context.state.div = $('<div/>')
	       .addClass("newtime-frame")
	       .css(
		 { position: 'absolute',
		   left: offset.left + parseInt(element.css('marginLeft')),
		   top: offset.top + element.outerHeight()
		 })
	       .bind('click',
		     function(e) { e.preventDefault(); return false; });
	     $.newtime_create(options, context);
	     element.after(context.state.div);
	     e.preventDefault();
	     $.popupManager.show(context.state.div);
	     return false;
	   });
       });
   };

 })(jQuery);