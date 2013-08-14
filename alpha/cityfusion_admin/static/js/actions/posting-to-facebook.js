;(function($, window, document, undefined) {
    'use strict';

    var FacebookEventsPostingService = function() {
        var self = this;

        self.init = function() {
            self.tabsContainer = $(".tabs-container");
            self.postingLinkSelector = "[data-type=posting_link]";
            self.postingTrSelector = "[data-type=posting_tr]";
            self.postingStatusSelector = "[data-type=posting_status]";
            self.postingBox  = $("[data-id=posting_box]");
            self.miniIndicator = $("[data-id=mini_indicator]");

            self.postingUrl = self.postingBox.data("posting-url");

            self.postingBox.on("click", self.postingLinkSelector, self.onPostingLinkClick);
        };

        self.onPostingLinkClick = function() {
            var link = $(this);

            self.miniIndicator.insertAfter(link).show();
            var eventId = link.data("event-id");
            $.post(self.postingUrl, {
                "event_id": eventId,
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            }, function(data) {
                if(data.success) {
                    self.miniIndicator.hide();

                    link.closest(self.postingTrSelector)
                        .children(self.postingStatusSelector)
                        .html("Yes");

                    link.replaceWith($("<a/>", {
                        "href": "https://www.facebook.com/events/" + data.facebook_event_id + "/",
                        "text": "FB event link"
                    }));
                }
                else {
                    var message = $("<div/>", {
                        "class": "alert-error",
                        "html": data.text
                    }).insertBefore(self.tabsContainer)

                    window.setTimeout(function() {
                        message.remove();
                    }, 3000);
                }
            }, 'json');
        };

        self.init();
    };

    $(document).ready(function() {
        new FacebookEventsPostingService();
    });
})(jQuery, window, document);