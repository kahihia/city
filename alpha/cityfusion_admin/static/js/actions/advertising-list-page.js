;(function($, window, document, undefined) {
    'use strict';

    var AdvertisingListPage = function(){
        this.initSortable();
    }

    AdvertisingListPage.prototype = {
        initSortable: function() {
            $(".sortable").on("click", function(){
                window.location = window.filters.removeFilter("o").setFilter("o", $(this).data("order")).getURL();
            });

            setTimeout(function(){
                $(".sortable[data-order='"+window.filters.params.o+"'").addClass("active");
            }, 100);
        }       
    }        

    $(document).ready(function(){
        new AdvertisingListPage();
    });

})(jQuery, window, document);