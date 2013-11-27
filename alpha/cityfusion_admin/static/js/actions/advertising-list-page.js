;(function($, window, document, undefined) {
    'use strict';

    var AdvertisingListPage = function(){
        this.initSortable();
        this.initUserInputs();
    }

    AdvertisingListPage.prototype = {
        initSortable: function() {
            $(".show-all").on("click", function(){
                window.location = window.filters.clear().getURL();
            });

            $(".sortable").on("click", function(){
                window.location = window.filters.removeFilter("o").setFilter("o", $(this).data("order")).getURL();
            });

            setTimeout(function(){
                $(".sortable[data-order='"+window.filters.params.o+"'").addClass("active");
            }, 100);
        },
        initUserInputs: function() {
            $(".user-input").each(function(index, input){
                $(input).select2({
                    placeholder: "User name",
                    minimumInputLength: 2,
                    width: 150,
                    ajax: {
                        url: $(input).data("ajax-url"),
                        dataType: "json",
                        data: function (term, page) {
                            return { "search": term };
                        },
                        results: function (data) {
                            return {results: data};
                        }
                    },
                    formatResult: function(data) {
                        return "<span>" + data.name + "</span>";
                    },
                    formatSelection: function(data) {
                        return "<span>" + data.name + "</span>";
                    }
                });

                $(input).select2("data", {
                    "id": $(input).val(),
                    "name": $(input).data("user-name")
                });
            });
        },
    }        

    $(document).ready(function(){
        new AdvertisingListPage();
    });

})(jQuery, window, document);