;(function($, window, document, undefined) {
    'use strict';

    var UserenaService = function() {
        var self = this;

        self.init = function() {
            var inputSelector = ".userena-input input";

            $(inputSelector).each(function() {
                var obj = $(this);
                self.setInputEmpty(obj);
            });

            $("body").on("focus", inputSelector, self.onInputFocus);
            $("body").on("blur", inputSelector, self.onInputBlur);

            var firstInput = $(inputSelector).first();
            if(firstInput.parent().data("set-focus") === 1) {
                firstInput.focus();
            }
        }

        self.onInputFocus = function() {
            $(this).removeClass("empty");
        };

        self.onInputBlur = function() {
            var obj = $(this);
            self.setInputEmpty(obj);
        };

        self.setInputEmpty = function(obj) {
            obj.attr("placeholder", obj.parent().data("placeholder"));

            if(!obj.val()) {
                obj.addClass("empty");
            }
        };

        self.init();
    };

    $(document).on("ready page:load", function(){
        new UserenaService();
    });

})(jQuery, window, document);