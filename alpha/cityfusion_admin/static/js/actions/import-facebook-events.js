;(function($, window, document, undefined) {
    'use strict';

    var FacebookEventsService = function() {
        var self = this;

        self.init = function() {
            self.indicatorBlock = $("[data-id=indicator_block]");
            self.eventsBlock = $("[data-id=facebook_events_list]");
            self.searchButton = $("[data-id=search_button]");
            self.moreLink = $("[data-id=load_more]");
            self.placeInput = $(".location-text-box input");
            self.locationLayer = $("[data-id=location_layer]");


            self.loadUrl = self.eventsBlock.data("load-url");
            self.createUrl = self.eventsBlock.data("create-url");
            self.rejectUrl = self.eventsBlock.data("reject-url");

            self.locationElements = {
                "id_geo_street": "geo_street",
                "id_geo_venue": "geo_venue",
                "id_geo_address": "geo_address",
                "id_geo_country": "geo_country",
                "id_geo_city": "geo_city",
                "id_geo_latitude": "geo_latitude",
                "id_geo_longtitude": "geo_longtitude",
                "id_place": "place",
                "id_street": "street",
                "id_location_lng": "location_lng",
                "id_location_lat": "location_lat",
                "id_city_0": "city_0",
                "id_city_1": "city_1",
                "id_venue_name": "venue_name",
                "id_city_identifier": "city_identifier"
            };

            self.reset();

            self.searchButton.click(self.onSearchButtonClick);
            self.moreLink.click(self.onMoreLinkClick);

            self.eventsBlock.on("click", "[data-type=button_import]", self.onImportButtonClick);
            self.eventsBlock.on("click", "[data-type=button_reject]", self.onRejectButtonClick);

            $("body").on("click", "[data-id=location_button_cancel]", self.onLocationCancelButtonClick);
            $("body").on("click", "[data-id=location_button_ok]", self.onLocationOkButtonClick);

            $("body").prepend(self.locationLayer);
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
                        var message = $("<div/>", {
                            "class": "alert-error",
                            "html": data.text
                        });

                        self.eventsBlock.html(message);
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
            self.activeItem = $(this).closest("[data-type=event_item]");

            var buttons = $(this).parent().find("input");
            buttons.attr("disabled", "true");

            if($(this).attr("data-complete") === "true") {
                self.processImport();
            }
            else {
                self.resetLocationParams();
                self.locationLayer.show();
            }
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

        self.onLocationOkButtonClick = function() {
            self.locationLayer.hide();
            self.processImport();
        };

        self.onLocationCancelButtonClick = function() {
            self.locationLayer.hide();
            self.activeItem.find("input").removeAttr("disabled");
        };

        self.processImport = function() {
            var buttons = self.activeItem.find("input");

            var eventData = {
                "facebook_event_id": self.activeItem.data("event-id"),
                "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
            }

            $.each(self.locationElements, function(id, name) {
                eventData[name] = $("#" + id).val();
            });

            $.post(self.createUrl, eventData, function(data) {
                if(data.success) {
                    var message = $("<div/>", {
                        "class": "alert-success",
                        "html": "Import completed successfully"
                    }).insertBefore(self.activeItem);

                    self.activeItem.remove();
                    delete self.activeItem;
                }
                else {
                    var message = $("<div/>", {
                        "class": "alert-error",
                        "html": "Import error"
                    }).insertBefore(self.activeItem);

                    buttons.removeAttr("disabled");
                }

                window.setTimeout(function() {
                    message.remove();
                }, 3000);
            }, 'json');
        };

        self.resetLocationParams = function() {
            var elements = ["id_geo_street", "id_geo_venue", "id_geo_address",
                            "id_geo_country", "id_geo_city", "id_geo_latitude",
                            "id_geo_longtitude", "id_place", "id_street",
                            "id_location_lng", "id_location_lat", "id_city_0",
                            "id_city_1", "id_venue_name", "id_city_identifier"];

            $.each(self.locationElements, function(id, name) {
                $("#" + id).val("");
            });
        };

        self.init();
    };

    $(document).ready(function() {
        var locationSearch = new window.SearchByLocation();

        /// Monkey patching
        locationSearch.searchUrl = "/cf-admin/locations?search=";
        locationSearch.findByLocation = function(name, city) {
            $(".search-lists").hide();
            window.setTimeout(function() { // hack for list closing
                $(".search-lists").removeAttr("style");
            }, 100);

            $(".location-text-box input").val(city);
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
        ///

        new window.VenueAutocomplete();
        new FacebookEventsService();
    });
})(jQuery, window, document);