(function($) {

   function createHead() {
     var table = $('<table class="newcal-table"/>');
     var content = (
       '<thead>' +
	 '<tr>' +
	 '<td class="newcal-month-left">A</td>' +
	 '<td class="newcal-month" colspan="5">July 2011</td>' +
	 '<td class="newcal-month-right">B</td>' +
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

   function startOfThisMonth() {
     var date = new Date();
     var start = { 'day' : date.getDay(),
		   'month' : date.getMonth(),
		   'year' : date.getYear() };
     return start;
   }
   window.sotm = startOfThisMonth;

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
     var i, elem, html = [];
     for (i in row) {
       if (row.hasOwnProperty(i)) {
	 elem = row[i];
	 if (elem === '') {
	   html.push('<td class="newcal-noday"></td>');
	 } else {
	   html.push('<td class="newcal-day">' + elem + '</td>');
	 }
       }
     }
     return html.join('');
   }

   function createCalendarRows(options, rows) {
     var i, row, html = [];
     for (i in rows) {
       if (rows.hasOwnProperty(i)) {
	 html.push('<tr>');
	 html.push(createCalendarRow(options, rows[i]));
	 html.push('</tr>');
       }
     }
     return $(html.join(''));
   }
   
   function createTable(options) {
     return (createHead(options)
	     .append(createDays(options))
	     .append(createCalendarRows(options, createCalendarArrayRows(startOfThisMonth()))));
   };

   /***
    * Options for newcal:
    *   onClick: function(date) - function to call when a date is selected
    */
   $.fn.newcal = function(options) {
     return this.each(
       function() {
	 var div;
	 var element = $(this);
	 element.bind(
	   'click',
	   function(e) {
	     if (div) return true;
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
	     div.append( createTable(options) );
	     e.preventDefault();
	     return false;
	   });
	 $(document).bind(
	   'click',
	   function(e) {
	     div.hide();
	   });
       });
   };

 })(jQuery);