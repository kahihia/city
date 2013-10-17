;(function($, window, document, undefined) {
    'use strict';

    var AccountService = function() {
        var self = this;

        self.init = function() {
            self.clearGraphUrl = $("[data-type=hidden_elements] [data-id=clear_graph_url]").val();
            self.postToFBUrl = $("[data-type=hidden_elements] [data-id=post_to_facebook_url]").val();
            self.bindToVenueUrl = $("[data-type=hidden_elements] [data-id=bind_to_venue_url]").val();

            self.csrfToken = $("[data-type=hidden_elements] input[name=csrfmiddlewaretoken]").val();
            self.eventCheckTpl = $("[data-type=hidden_elements] [data-type=event_check]");
            self.facebookLinkTpl = $("[data-type=hidden_elements] [data-type=facebook_event_link]");

            self.eventItemSelector = "[data-type=event_item]";
            self.eventCheckerSelector = "[data-type=event_check]";
            self.facebookLinkSelector = "[data-type=facebook_event_link]";
            self.executeButtonSelector = "[data-id=execute_button]";
            self.actionSelector = "[data-id=action_select]";
            self.eventContainer = $("[data-id=event_container]");
            self.venueSelect = $("[data-id=venue_select]");
            self.miniIndicator = $("[data-id=mini_indicator]");

            self.executeBusy = false;

            $("body").on("click", self.executeButtonSelector, self.onExecuteButtonClick);
            $("body").on("change", self.eventCheckerSelector, self.onEventCheckboxChange);
            $("body").on("change", self.actionSelector, self.onActionSelectChange);

            self.reset();
            self.makeCheckBoxesForFBPosting();
        }

        self.onExecuteButtonClick = function() {
            if(!self.executeBusy) {
                $(self.actionSelector).prop("disabled", true);

                self.executeBusy = true;
                self.reset();

                var action = $(self.actionSelector).val();
                var button = $(this);

                if(action === "post_selected_to_fb") {
                    self.postToFB(button);
                }
                else if(action === "bind_selected_to_venue") {
                    self.bindToVenue(button);
                }
            }
        };

        self.onActionSelectChange = function() {
            var value = $(this).val();

            if(value === "post_selected_to_fb") {
                self.makeCheckBoxesForFBPosting();
            }
            else if(value === "bind_selected_to_venue") {
                self.makeCheckBoxesForEventTransferring();
            }
        };

        self.onEventCheckboxChange = function() {
            var eventId = $(this).data("event-id");
            $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]")
                .not(this).
                removeAttr("checked");
        };

        self.postToFB = function(button) {
            self.checkFBLogin(function() {
//                if($.fancybox) {
//                    $.fancybox($("#choice-window"));
//                }
                var checkedEvents = $(self.eventCheckerSelector + ":checked");
                if(checkedEvents.length !== 0) {
                    self.miniIndicator.show().insertAfter(button);
                    self.eventsToProcessCount = checkedEvents.length;

                    var ids = [];
                    $.each(checkedEvents, function() {
                        ids.push($(this).data("event-id"));
                    });

                    self.executeFBPosting(ids);
                }
                else {
                    self.executeBusy = false;
                    $(self.actionSelector).prop("disabled", false);
                }
            });
        };

        self.bindToVenue = function(button) {
            self.venueSelect.prop("disabled", true);

            var checkedEvents = $(self.eventCheckerSelector + ":checked");
            if(checkedEvents.length !== 0) {
                self.miniIndicator.show().insertAfter(button);
                self.eventsToProcessCount = checkedEvents.length;

                var ids = [];
                $.each(checkedEvents, function() {
                    ids.push($(this).data("event-id"));
                });

                self.executeBindingToVenue(ids);
            }
            else {
                self.executeBusy = false;
                $(self.actionSelector).prop("disabled", false);
                self.venueSelect.prop("disabled", false);
            }
        };

        self.executeFBPosting = function(eventIds) {
            if(eventIds.length !== 0) {
                var eventId = eventIds.shift();
                $.post(self.postToFBUrl, {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId
                }, function(data) {
                    if(data.success) {
                        var message = self.createSuccessMessage();
                        self.successProcessCount++;
                        message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events posted to Facebook.");

                        $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]").each(function() {
                            var link = self.facebookLinkTpl.clone();
                            link.attr("href", "https://www.facebook.com/events/" + data.facebook_event_id + "/");

                            $(this).parent().attr("data-facebook-event-id", data.facebook_event_id);
                            $(this).replaceWith(link);
                        });
                    }
                    else {
                        var errorHtml = "Error while event posting: \"" + data.error + "\".";
                        if(data.event_link) {
                            errorHtml += " <a target='_blank' href='"+ data.event_link + "'>Link to the event</a>.";
                        }

                        var message = $("<div/>", {
                            "class": "alert-error",
                            "html": errorHtml
                        });

                        self.eventContainer.prepend(message);
                    }

                    self.executeFBPosting(eventIds);
                }, 'json');
            }
            else {
                self.miniIndicator.hide();
                self.executeBusy = false;
                $(self.actionSelector).prop("disabled", false);

                var message = self.createSuccessMessage();
                message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events posted to Facebook. "
                                              + "Operation complete!<br/>"
                                              + "You're welcome to edit your events on Facebook "
                                              + "to add their photos (just click the icon on the left of the "
                                              + "necessary event).");
            }
        };

        self.executeBindingToVenue = function(eventIds) {
            if(eventIds.length !== 0) {
                var eventId = eventIds.shift();
                var venueAccountId = self.venueSelect.val();
                $.post(self.bindToVenueUrl, {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId,
                    "venue_account_id": venueAccountId
                }, function(data) {
                    if(data.success) {
                        var message = self.createSuccessMessage();
                        self.successProcessCount++;
                        message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events bound to the venue.");
                    }
                    else {
                        var message = $("<div/>", {
                            "class": "alert-error",
                            "html": "Error while event binding: \"" + data.error + "\""
                        });

                        self.eventContainer.prepend(message);
                    }

                    self.executeBindingToVenue(eventIds);
                }, 'json');
            }
            else {
                self.miniIndicator.hide();
                self.executeBusy = false;
                $(self.actionSelector).prop("disabled", false);
                self.venueSelect.prop("disabled", false);

                var message = self.createSuccessMessage();
                message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events bound to the venue. "
                                              + "Operation complete!");
            }
        };

        self.checkFBLogin = function(successCallback) {
            if(typeof(FB) === "undefined") {
                alert("Facebook library isn't ready yet. Please, wait.");
                return;
            }

            FB.login(function(response) {
                if (response.authResponse) {
                    $.post(self.clearGraphUrl, {
                        "csrfmiddlewaretoken": self.csrfToken
                    }, function(data) {
                       if(data.success) {
                           successCallback();
                       }
                    }, 'json');
                }
            }, {scope: 'create_event'});
        };

        self.makeCheckBoxesForFBPosting = function() {
            self.venueSelect.hide();

            $(self.eventItemSelector).each(function() {
                var facebookEventId = $(this).data("facebook-event-id");
                if(facebookEventId) {
                    var link = self.facebookLinkTpl.clone();
                    link.attr("href", "https://www.facebook.com/events/" + facebookEventId + "/");

                    $(this).find(self.eventCheckerSelector + "," + self.facebookLinkSelector).remove();
                    $(this).prepend(link);
                }
                else {
                    var eventId = $(this).data("event-id");
                    var check = self.eventCheckTpl.clone();
                    check.attr("data-event-id", eventId);

                    var existingCheck = $(this).find(self.eventCheckerSelector + ":checked");
                    if(existingCheck.length !== 0) {
                        check.prop("checked", true);
                    }

                    $(this).find(self.eventCheckerSelector + "," + self.facebookLinkSelector).remove();
                    $(this).prepend(check);
                }
            });
        };

        self.makeCheckBoxesForEventTransferring = function() {
            self.venueSelect.show();

            $(self.eventItemSelector).each(function() {
                    var eventId = $(this).data("event-id");
                    var check = self.eventCheckTpl.clone();
                    check.attr("data-event-id", eventId);

                    var existingCheck = $(this).find(self.eventCheckerSelector + ":checked");
                    if(existingCheck.length !== 0) {
                        check.prop("checked", true);
                    }

                    $(this).find(self.eventCheckerSelector + "," + self.facebookLinkSelector).remove();
                    $(this).prepend(check);
            });
        };

        self.createSuccessMessage = function() {
            var message = $("[data-id=success_process_message]");
            if(message.length === 0) {
                var message = $("<div/>", {
                    "class": "alert-success",
                    "data-id": "success_process_message"
                });

                self.eventContainer.prepend(message);
            }

            return message;
        };

        self.reset = function() {
            self.eventsToProcessCount = 0;
            self.successProcessCount = 0;
        };

        self.init();
    };

    $(document).on("ready page:load", function(){
        new AccountService();
    });

})(jQuery, window, document);