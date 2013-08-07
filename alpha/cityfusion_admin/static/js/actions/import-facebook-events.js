;(function($, window, document, undefined) {
    'use strict';

    var FacebookEventsLoader = function() {
        var self = this;

        self.init = function() {
            self.indicatorBlock = $("[data-id=indicator_block]");
            self.eventsBlock = $("[data-id=facebook_events_list]");
            self.searchButton = $("[data-id=search_button]");
            self.moreLink = $("[data-id=load_more]");
            self.placeInput = $(".location-text-box input");

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
            self.place = self.placeInput.attr("data-city");

            self.loadEvents({"place": self.place}, function() {
                self.eventsBlock.empty();
                $(".form-block").append(self.indicatorBlock.show());
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
    };

    $(document).ready(function() {
        var locationSearch = new window.SearchByLocation();
        locationSearch.searchUrl = "/cf-admin/locations?search=";
        locationSearch.findByLocation = function(name, city) {
            $(".search-lists").hide();
            window.setTimeout(function() { // hack for list closing
                $(".search-lists").removeAttr("style");
            }, 100);

            $(".location-text-box input").val(name);
            $(".location-text-box input").attr("data-city", city);
        };

        locationSearch.initLocationLinks = function() {
            var that=this;
            $("li a", this.searchList).each(function(){
                $(this).on("click", function() {
                    that.findByLocation(
                        $(this).text(),
                        $(this).data("location-city")
                    );
                });
            });
        },

        locationSearch.appendLink = function(data) {
            var link, li;

            link = $("<a href='javascript:void(0);'>").html(data.name);
            link.attr("data-location-city", data.city_name);

            li = $("<li>").append(link);
            return li;
        }

        new FacebookEventsLoader();
    });
})(jQuery, window, document);