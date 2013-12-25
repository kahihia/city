;(function($, window, document, undefined) {
    'use strict';

    var StaticPagesService = function() {
        var self = this;

        self.init = function() {
            self.entryTextSelector = "[data-type=entry_text]";
            $("[data-type=entry_title]").click(self.onEntryTitleClick);
        };

        self.onEntryTitleClick = function() {
            $(this).next(self.entryTextSelector).toggle();
        };

        self.init();
    };

    $(document).ready(function() {
        new StaticPagesService();
    });
})(jQuery, window, document);