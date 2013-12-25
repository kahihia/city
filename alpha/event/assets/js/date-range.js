;(function($, window, document, undefined) {

    function DateRange(startDate, endDate, nextDay) {
         $(startDate).datepicker({
            minDate: new Date(),
            onSelect: function (date) {
                var date1 = $(startDate).datepicker('getDate'),
                    date2 = $(endDate).datepicker('getDate');

                if(date2 && date1>date2) {
                    if(nextDay){
                        date2.setDate(date1.getDate() + 1);
                    } else {
                        date2.setDate(date1.getDate());
                    }

                    $(endDate).datepicker('setDate', date2);
                }

                $(endDate).datepicker('option', 'minDate', date1);
            }
        });

        $(endDate).datepicker({
            minDate: new Date(),
            onClose: function () {
                var date1 = $(startDate).datepicker('getDate');
                var date2 = $(endDate).datepicker('getDate');
                //check to prevent a user from entering a date below date of date1
                if (date2 <= date1) {
                    var minDate = $(endDate).datepicker('option', 'minDate');
                    $(endDate).datepicker('setDate', minDate);
                }
            }
        });
    }

    window.DateRange = DateRange;
})(jQuery, window, document);   