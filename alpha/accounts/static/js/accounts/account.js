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
            self.fbPagesSelect = $("[data-id=fb_pages_select]");
            self.fbChoiceWindow = $("[data-id=choice_window]");
            self.fbPostOkSelector = "[data-id=fb_post_ok]";
            self.fbOwnerTypeSelector = "[data-type=fb_owner_type]";
            self.selectAllSelector = "[data-id=select_all_button]";

            self.executeBusy = false;

            $("body").on("click", self.executeButtonSelector, self.onExecuteButtonClick);
            $("body").on("change", self.actionSelector, self.onActionSelectChange);
            $("body").on("click", self.fbOwnerTypeSelector, self.onFBOwnerTypeRadioClick);
            $("body").on("click", self.fbPostOkSelector, self.onPostFBOkClick);
            $("body").on("click", self.selectAllSelector, self.onSelectAllButtonClick);

            self.reset();
            self.makeCheckBoxesForFBPosting();
            self.initBalloons();
        }

        self.onExecuteButtonClick = function() {
            if(!self.executeBusy) {
                var checkedEvents = $(self.eventCheckerSelector + ":checked");
                if(checkedEvents.length !== 0) {

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

        self.onFBOwnerTypeRadioClick = function() {
            var fbOwnerType = $(this).val();
            if(fbOwnerType === "page") {
                self.fbPagesSelect.show();
            }
            else {
                self.fbPagesSelect.hide();
            }
        };

        self.onPostFBOkClick = function() {
            if($.fancybox) {
                self.fancyBox.endProcessOnClose = false;
                $.fancybox.close();

                var checkedEvents = $(self.eventCheckerSelector + ":checked");
                if(checkedEvents.length !== 0) {
                    self.miniIndicator.show().insertAfter($(self.executeButtonSelector));

                    var ids = [];
                    $.each(checkedEvents, function() {
                        var eventId = $(this).data("event-id");
                        if($.inArray(eventId, ids) === -1) {
                            ids.push(eventId);
                        }
                    });

                    self.eventsToProcessCount = ids.length;
                    self.executeFBPosting(ids);
                }
                else {
                    self.finishPostToFB();
                }

            }
        };

        self.onSelectAllButtonClick = function() {
            var checked = parseInt($(this).attr("data-checked"));
            if(!checked) {
                $(this).attr("data-checked", 1);
                $(self.eventCheckerSelector).not(self.eventCheckTpl).prop("checked", true);
            }
            else {
                $(this).attr("data-checked", 0);
                $(self.eventCheckerSelector).prop("checked", false);
            }
        };

        self.postToFB = function(button) {
            self.checkFBLogin(function() {
                var checkedEvents = $(self.eventCheckerSelector + ":checked");
                if($.fancybox) {
                    $.fancybox(self.fbChoiceWindow, {
                        "beforeLoad": function() {
                            self.fancyBox = this;
                            self.fancyBox.endProcessOnClose = true;
                            if(self.fbPagesSelect.children().length === 0) {
                                FB.api('/me/accounts', { limit: 100 }, function(response) {
                                    var pages = response.data;
                                    $.each(pages, function() {
                                        self.fbPagesSelect.append($("<option/>", {
                                            "value": this.id,
                                            "text": this.name
                                        }));
                                    });
                                });
                            }
                        },
                        "afterClose": function() {
                            if(self.fancyBox.endProcessOnClose) {
                                self.finishPostToFB();
                            }
                        },
                        scrolling: "visible"
                    });
                }
                else {
                    self.finishPostToFB();
                }
            });
        };

        self.finishPostToFB = function() {
            self.executeBusy = false;
            $(self.actionSelector).prop("disabled", false);
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
                var data = {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId
                }

                data["owner_type"] = $("[data-type=fb_owner_type]:checked").val();
                if(data["owner_type"] === "page") {
                    data["page_id"] = self.fbPagesSelect.val();
                }

                $.post(self.postToFBUrl, data, function(data) {
                    if(data.success) {
                        var message = self.createSuccessMessage();
                        self.successProcessCount++;
                        message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events posted to Facebook.");

                        var index = 0;
                        $.each(data.facebook_event_ids, function(singleEventId, fbEventId) {
                            var checker = $(self.eventCheckerSelector + "[data-single-event-id=" + singleEventId + "]");
                            if(checker.length === 0 && index === 0) {
                                var eventChecker = $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]");
                                if(!data.facebook_event_ids[eventChecker.attr("single-event-id")]) {
                                    checker = eventChecker;
                                }
                            }

                            var link = self.facebookLinkTpl.clone();
                            link.attr("href", "https://www.facebook.com/events/" + fbEventId + "/");

                            checker.parent().attr("data-facebook-event-id", fbEventId);
                            checker.replaceWith(link);

                            index++;
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
                self.finishPostToFB();

                var message = self.createSuccessMessage();
                message.html(self.successProcessCount + " out of " + self.eventsToProcessCount
                                              + " events posted to Facebook. "
                                              + "Operation complete!");
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

                        var elem = $(self.eventItemSelector + "[data-event-id=" + eventId + "]")
                                    .find("[data-type=venue_title]");
                        var text = self.venueSelect.text();
                        var link = $('option:selected', self.venueSelect).data("venue-link");
                        elem.html("by <a href='" + link + "'>" + text + "</a>");
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
                    var singleEventId = $(this).data("single-event-id");
                    var check = self.eventCheckTpl.clone();
                    check.attr("data-event-id", eventId);
                    check.attr("data-single-event-id", singleEventId);

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

        self.initBalloons = function(){
            $.balloon.defaults.classname = "hintbox";
            $.balloon.defaults.css = {};
            var ballons = $(".balloon");
            $(ballons).each(function(){
                var content = $(this).siblings(".balloon-content").clone().show();
                $(this).balloon({
                    contents:content,
                    position:"top",
                    tipSize: 0,
                    offsetX:0,//$.browser.msie?0:25,
                    offsetY:10,//$.browser.msie?25:0,
                    showDuration: 500, hideDuration: 0,
                    showAnimation: function(d) { this.fadeIn(d); }
                });
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