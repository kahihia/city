;(function($, window, document, undefined) {
    'use strict';

    var FacebookEventsLoader = function() {
        var self = this;

        self.init = function() {
            self.indicatorBlock = $("[data-id=indicator_block]");
            self.eventsBlock = $("[data-id=facebook_events_list]");
            self.searchButton = $("[data-id=search_button]");
            self.moreLink = $("[data-id=load_more]");
            self.placeInput = $("[data-id=place_input]");

            self.loadUrl = self.eventsBlock.data("load-url");
            self.createUrl = self.eventsBlock.data("create-url");
            self.rejectUrl = self.eventsBlock.data("reject-url");

            self.reset();

            self.searchButton.click(self.onSearchButtonClick);
            self.moreLink.click(self.onMoreLinkClick);

            self.eventsBlock.on("click", "[data-type=button_import]", self.onImportButtonClick);
            self.eventsBlock.on("click", "[data-type=button_reject]", self.onRejectButtonClick);
        };

        self.reset = function() {
            self.place = null;
            self.page = 0;
        };

        self.loadEvents = function(params, beforeAction) {
            self.searchButton.attr("disabled", "true");
            beforeAction();
            $.get(self.loadUrl,
                params,
                function(data) {
                    if(data.success) {
                        self.eventsBlock.append(data.content);
                        if(data.page) {
                            self.page = data.page;
                            self.moreLink.show();
                        }
                        else {
                            self.moreLink.hide();
                        }
                    }
                    else {
                        self.eventsBlock.html(data.text);
                        self.moreLink.hide();

                        self.reset();
                    }

                    self.indicatorBlock.hide();
                    self.searchButton.removeAttr("disabled");
                },
                'json'
            );
        };

        self.onSearchButtonClick = function() {
            self.place = self.placeInput.val();

            self.loadEvents({"place": self.place}, function() {
                self.eventsBlock.empty();
                self.indicatorBlock.insertAfter(self.searchButton).show();
                self.moreLink.hide();
            });
        };

        self.onMoreLinkClick = function() {
            if(self.place) {
                self.loadEvents({
                    "place": self.place,
                    "page": self.page
                }, function() {
                    self.moreLink.append(self.indicatorBlock.show());
                });
            }
        };

        self.onImportButtonClick = function() {
            var buttons = $(this).parent().find("input");
            buttons.attr("disabled", "true");

            var eventData = {
                "facebook_event_id": $(this).closest("[data-type=event_item]").data("event-id"),
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            }

            var eventItem = $(this).closest("[data-type=event_item]");

            $.post(self.createUrl, eventData, function(data) {
                if(data.success) {
                    var message = $("<div/>", {
                        "class": "alert-success",
                        "html": "Import completed successfully"
                    }).insertBefore(eventItem);

                    eventItem.remove();
                }
                else {
                    var message = $("<div/>", {
                        "class": "alert-error",
                        "html": "Import error"
                    }).insertBefore(eventItem);

                    buttons.removeAttr("disabled");
                }

                window.setTimeout(function() {
                    message.remove();
                }, 3000);
            }, 'json');
        };

        self.onRejectButtonClick = function() {
            var buttons = $(this).parent().find("input");
            buttons.attr("disabled", "true");

             var eventData = {
                "facebook_event_id": $(this).closest("[data-type=event_item]").data("event-id"),
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            }

            var eventItem = $(this).closest("[data-type=event_item]");
            $.post(self.rejectUrl, eventData, function(data) {
                if(data.success) {
                    eventItem.remove();
                }
            }, 'json');
        };

        self.init();
    }

    $(document).ready(function() {
        new FacebookEventsLoader();
    });
})(jQuery, window, document);