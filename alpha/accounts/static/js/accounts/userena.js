;(function($, window, document, undefined) {
    'use strict';

    var UserenaService = function() {
        var self = this;

        self.init = function() {
            var usernameSelector = ".user-identification input";
            var passwordSelector = ".user-password input";

            var selectors = [usernameSelector, passwordSelector].join(",");
            $(selectors).each(function() {
                var obj = $(this);
                self.setInputEmpty(obj);
            });

            $("body").on("focus", selectors, self.onInputFocus);
            $("body").on("blur", selectors, self.onInputBlur);
        }

        self.onInputFocus = function() {
            $(this).attr("placeholder", "");
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