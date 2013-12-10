;(function($, window, document, undefined) {
    'use strict';

    var FacebookEventsImportService = function() {
        var self = this;

        self.init = function() {
            self.formBlock = $("[data-id=form_block]");
            self.indicatorBlock = $("[data-id=indicator_block]");
            self.miniIndicator = $("[data-id=mini_indicator]");
            self.eventsBlock = $("[data-id=facebook_events_list]");
            self.searchButton = $("[data-id=search_button]");
            self.moreLink = $("[data-id=load_more]");
            self.cityInput = $("[data-id=city_input]");
            self.cityName = $("[data-id=city_name]");
            self.fbPageInput = $("[data-id=fb_page_url]");
            self.fancyboxSelector = ".fancybox-wrap";
            self.formErrorsTplSelector = "[data-id=form_errors_tpl]";
            self.formErrorsItemsSelector = "[data-type=form_errors_items]";
            self.formErrorItemSelector = "[data-type=form_error_item]";


            self.loadUrl = self.eventsBlock.data("load-url");
            self.createUrl = self.eventsBlock.data("create-url");
            self.rejectUrl = self.eventsBlock.data("reject-url");
            self.clearGraphUrl = self.eventsBlock.data("graph-clear-url");

            self.reset();
            self.initCityInput();

            self.searchButton.click(self.onSearchButtonClick);
            self.moreLink.click(self.onMoreLinkClick);

            self.eventsBlock.on("click", "[data-type=button_import]", self.onImportButtonClick);
            self.eventsBlock.on("click", "[data-type=button_reject]", self.onRejectButtonClick);
        };

        self.reset = function() {
            self.place = null;
            self.page = 0;
        };

        self.initCityInput = function() {
            self.cityInput.select2({
                placeholder: "City name",
                minimumInputLength: 2,
                ajax: {
                    url: self.cityInput.data("ajax-url"),
                    dataType: "json",
                    data: function (term, page) {
                        return {"search": term};
                    },
                    results: function (data) {                    
                        return {results: data};
                    }
                },
                formatResult: function(data) {
                    return "<span>" + data.name + "</span>";
                },
                formatSelection: function(data) {
                    return "<span>" + data.city_name + "</span>";
                }
            });

            self.cityInput.on("change", function(e) {            
                self.cityName.val(e.added.city_name);
            })
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
            self.checkFBLogin(function() {
                self.place = self.cityName.val();
                self.fbPageUrl = self.fbPageInput.val();

                $("#id_tags__tagautosuggest").data('ui-tagspopup').forCity(self.cityName.val());

                self.loadEvents({
                    "place": self.place,
                    "fb_page_url": self.fbPageUrl
                }, function() {
                    self.eventsBlock.empty();
                    $(".form-block").append(self.indicatorBlock.show());
                    self.moreLink.hide();
                });
            });
        };

        self.onMoreLinkClick = function() {
            self.checkFBLogin(function() {
                if(self.place) {
                    self.loadEvents({
                        "place": self.place,
                        "fb_page_url": self.fbPageUrl,
                        "page": self.page
                    }, function() {
                        self.moreLink.append(self.indicatorBlock.show());
                    });
                }
            });
        };

        self.onImportButtonClick = function() {
            self.activeItem = $(this).closest("[data-type=event_item]");
            var buttons = $(this).parent().find("input");

            self.checkFBLogin(function() {
                buttons.attr("disabled", "true");

                if($.fancybox) {
                    var eventData = {
                        "facebook_event_id": self.activeItem.data("event-id"),
                        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
                    }

                    $.fancybox.open([
                        {
                            type: 'iframe',
                            href : self.createUrl + "?" + self.prepareUrlParams(eventData),
                            closeClick  : false,
                            helpers     : {
                                overlay : {closeClick: false}
                            }
                        }
                    ], {
                        afterLoad: function() {
                            var venueField = $(self.fancyboxSelector + " iframe").contents().find("#id_place");
                            var eventLocationName = self.activeItem.data("event-location");
                            if(!venueField.val() && eventLocationName) {
                                venueField.attr("placeholder", eventLocationName);
                            }

                            $(self.fancyboxSelector + " iframe").contents()
                                                                .find("[data-id=event_submit]").click(self.onSubmitButtonClick);
                        },
                        afterClose: function() {
                            buttons.removeAttr("disabled");
                        }
                    });
                }
            });
        };

        self.onSubmitButtonClick = function() {
            var button = $(this);
            var existing_form = button.closest("form");
            var sent_form = existing_form.clone();
            var tags_as_string = sent_form.find("#as-values-id_tags__tagautosuggest").val();

            sent_form.find("#id_tags").val(tags_as_string);
            sent_form.find("#id_tags__tagautosuggest").remove();

            var event_data = sent_form.serializeArray();
            event_data.push({
                "name": "facebook_event_id",
                "value": self.activeItem.data("event-id")
            });

            $.post(self.createUrl, event_data, function(data) {
                sent_form = null;
                if(data.success) {
                    $.fancybox.close();

                    var message = $("<div/>", {
                        "class": "alert-success",
                        "html": "Import completed successfully"
                    }).insertBefore(self.activeItem);

                    self.activeItem.remove();
                    delete self.activeItem;

                    window.setTimeout(function() {
                        message.remove();
                    }, 3000);
                }
                else {
                    var errors = button.closest("body").find(self.formErrorsTplSelector)
                                       .clone().removeAttr("data-id")
                                       .attr("data-type", "new_form_errors");
                    var errorsItems = errors.find(self.formErrorsItemsSelector);
                    var errorItem = errors.find(self.formErrorItemSelector);

                    errorsItems.empty();
                    $.each(data.info, function(key, value) {
                        var newErrorItem = errorItem.clone();
                        newErrorItem.find("span").text(value[0]);
                        errorsItems.append(newErrorItem);
                    });


                    existing_form.find("[data-type=new_form_errors]").remove();
                    existing_form.prepend(errors.show());

                    $(self.fancyboxSelector + " iframe").contents()
                        .find("html, body").animate({ scrollTop: 0 }, 10);
                }

            }, 'json');

            return false;
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

        self.prepareUrlParams = function(data) {
            var params = [];
            $.each(data, function(key, value) {
                params.push(key + "=" + value);
            });

            return params.join("&");
        };

        self.checkFBLogin = function(successCallback) {
            if(typeof(FB) === "undefined") {
                alert("Facebook library isn't ready yet. Please, wait.");
                return;
            }

            FB.login(function(response) {
                if (response.authResponse) {
                    $.post(self.clearGraphUrl, "", function(data) {
                       if(data.success) {
                           successCallback();
                       }
                    }, 'json');
                }
            });
        };

        self.init();
    };

    $(document).ready(function() {
        new window.VenueAutocomplete();
        new FacebookEventsImportService();
    });
})(jQuery, window, document);