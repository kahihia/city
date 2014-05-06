;(function($, window, document, undefined) {
    'use strict';

    function AccountEditPage(){
        var that=this;
        $("#id_not_from_canada").on("click", function(){
            that.showOrHideRegionField();
        });

        this.showOrHideRegionField();
        this.initFacebookPagesField();
    }

    AccountEditPage.prototype = {
        showOrHideRegionField: function(){
            if($("#id_not_from_canada").is(':checked')) {
                $(".native-region-tr").hide();
            } else {
                $(".native-region-tr").show();
            }
        },

        initFacebookPagesField: function() {
            $("body").on("click", "[data-type=fb_page_add]", function() {
                if($("[data-type=fb_page_item]").length < 5) {
                    $("<input type='text' name='fb_page[]' data-type='fb_page_item' />\n" +
                        "<input type='button' value='-' data-type='fb_page_del' />").insertBefore(this);
                    $("<br/>").insertBefore(this);
                }
            });

            $("body").on("click", "[data-type=fb_page_del]", function() {
                $(this).next("br").remove();
                $(this).prev("input").remove();
                $(this).remove();
            });
        }
    };

    $(document).on("ready page:load", function(){
        window.accountEditPage = new AccountEditPage();
    });

})(jQuery, window, document);