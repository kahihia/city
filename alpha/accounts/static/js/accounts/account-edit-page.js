;(function($, window, document, undefined) {
    'use strict';

    function AccountEditPage(){
        var that=this;
        $("#id_not_from_canada").on("click", function(){
            that.showOrHideRegionField();
        });

        this.showOrHideRegionField();
    }

    AccountEditPage.prototype = {
        showOrHideRegionField: function(){
            if($("#id_not_from_canada").is(':checked')) {
                $(".native-region-tr").hide();
            } else {
                $(".native-region-tr").show();
            }
        }       
    };

    $(document).on("ready page:load", function(){
        window.accountEditPage = new AccountEditPage();
    });

})(jQuery, window, document);