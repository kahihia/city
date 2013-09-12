;(function($, window, document, undefined) {
    'use strict';

    var ChangeEventOwnerPage = function(){
        this.initUserInputs();
    }

    ChangeEventOwnerPage.prototype = {
        initUserInputs: function() {
            $(".user-input").each(function(index, input){
                $(input).select2({
                    placeholder: "User name",
                    minimumInputLength: 2,
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
            });
        }
    }        

    $(document).ready(function(){
        new ChangeEventOwnerPage();
    });

})(jQuery, window, document);