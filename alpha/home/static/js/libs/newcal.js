(function($) {

   function createHead() {
     var table = $('<table class="newcal-table"/>');
     var content = (
       '<thead>' +
	 '<tr>' +
	 '<td class="newcal-month-left">&laquo;</td>' +
	 '<td class="newcal-month" colspan="5">July 2011</td>' +
	 '<td class="newcal-month-right">&raquo;</td>' +
	 '</tr>' +
	 '</thead>');
     table.html( content );
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
     var start = { 'day' : date.getDay(),
		   'month' : date.getMonth(),
		   'year' : date.getYear() + 1900};
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
       now = new Date(now.getYear(), now.getMonth(), now.getDate() + 1);
     }
     while (current.length < 7) {
       current.push('');
     }
     return rows;
   }
   window.ccar = createCalendarArrayRows;

   function createCalendarRow(options, row) {
     var i, elem, entries = $(), cell;
     for (i in row) {
       if (row.hasOwnProperty(i)) {
	 elem = row[i];
	 if (elem === '') {
	   entries = entries.add( $('<td class="newcal-noday"></td>'));
	 } else {
	   cell = $('<td class="newcal-day">' + elem + '</td>')
	     .bind(
	       'click',
	       (function(day) {
		 return function() { 
		   var date = new Date(options.startOfMonth.year,
				       options.startOfMonth.month,
				       day);
		   console.log("Going to", date);
		   if (options['onClick']) {
		     options.onClick(date);
		   }
		 };
		}(elem)));
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
     console.log(outrows);
     return outrows;
   }
   
   function createTable(options) {
     return (createHead(options)
	     .append(createDays(options))
	     .append(createCalendarRows(options, createCalendarArrayRows(options.startOfMonth))));
   };

   $.fn.newcal_fill = function(options) {
     options = options || {};
     options.startOfMonth = options.startOfMonth || startOfMonth();
     return this.each(
       function() {
	 var div = $(this);
	 div.children().remove();
	 div.append( createTable(options));
	 div.find('.newcal-month-left').bind(
	   'click', 
	   function() {
	     var prev_month = startOfMonth(new Date(options.startOfMonth.year, options.startOfMonth.month - 1, 1));
	     var new_options = $.extend(true, {}, options);
	     new_options.startOfMonth = prev_month;
	     div.newcal_fill(new_options);
	   });
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
	 var div;
	 var element = $(this);
	 element.bind(
	   'click',
	   function(e) {
	     if (div) return false;
	     var offset = element.position();
	     var padding = element.css('padding-left');
	     div = $('<div />')
	       .addClass('newcal-date-popup')
	       .css(
		 { position: 'absolute',
		   left: offset.left,
		   top: offset.top + element.height()
		 })
	       .bind('click', function(e) { e.stopPropagation(); e.preventDefault(); return false; });
	     element.after(div);
	     e.preventDefault();
	     div.newcal_fill(options);
	     return false;
	   });
	 $(document).bind(
	   'click',
	   function(e) {
	     if (div) {
	       div.hide();
	       div = null;
	     }
	   });
       });
   };

   function jumpToDate(date) {
     window.location = sprintf("/events/all/%04d-%02d-%02d", date.getYear() + 1900,
			       date.getMonth() + 1, date.getDate());
   }
   window.jumpToDate = jumpToDate;

 })(jQuery);