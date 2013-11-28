;(function($, window, document, undefined) {

	function NewMonthPicker(element, onSelect){
		var that = this,
            date;

        this.element = element;

        date = new Date();
        id = "mp_" + (+Date.now());

        this.monthValue = dom("input", {"class": "hidden monthpicker", "data-month-id": id});
        this.selectWrapper = dom("div", {"class": "wrapper"}, [
            this.label = dom("span", {"innerHTML": "Select More Months"}),
            this.selectButton = dom("div", {"class": "new-month-select-arrow"})
        ]);

        $(this.element).append(this.monthValue).append(this.selectWrapper);

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

            onSelect && onSelect(year, month);
        });
	}

	this.NewMonthPicker = NewMonthPicker;	

})(jQuery, window, document);	