;(function($, window, document, undefined) {
    'use strict';

    var BonusCampaignsPage = function(){
        this.initDatePickers();
    }

    BonusCampaignsPage.prototype = {
        initDatePickers: function() {
            $("#id_start_time").datepicker({
                onSelect: function (date) {
                    var date2 = $("#id_start_time").datepicker('getDate');
                    date2.setDate(date2.getDate());
                    //sets minDate to dt1 date + 1
                    $("#id_end_time").datepicker('option', 'minDate', date2);
                }
            });

            $("#id_end_time").datepicker({
                onClose: function () {
                    var dt1 = $("#id_start_time").datepicker('getDate');
                    var dt2 = $("#id_end_time").datepicker('getDate');
                    //check to prevent a user from entering a date below date of dt1
                    if (dt2 <= dt1) {
                        var minDate = $("#id_end_time").datepicker('option', 'minDate');
                        $("#id_end_time").datepicker('setDate', minDate);
                    }
                }
            });
        }
    }        

    $(document).ready(function(){
        new BonusCampaignsPage();
    });

})(jQuery, window, document);