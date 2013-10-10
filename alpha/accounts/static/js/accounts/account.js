;(function($, window, document, undefined) {
    'use strict';

    var AccountService = function() {
        var self = this;

        self.init = function() {
            self.clearGraphUrl = $("[data-type=hidden_elements] [data-id=clear_graph_url]").val();
            self.postFBUrl = $("[data-type=hidden_elements] [data-id=post_to_facebook_url]").val();

            self.csrfToken = $("[data-type=hidden_elements] input[name=csrfmiddlewaretoken]").val();
            self.eventCheckerSelector = "[data-type=event_check]";
            self.postFBButtonSelector = "[data-id=fb_post_button]";
            self.miniIndicator = $("[data-id=mini_indicator]");
            self.multipostFBBusy = false;
            self.eventsToPostCount = 0;
            self.successPostCount = 0;

            $("body").on("click", self.postFBButtonSelector, self.onFBPostButtonClick);
            $("body").on("change", self.eventCheckerSelector, self.onEventCheckboxChange);
        }

        self.onFBPostButtonClick = function() {
            var button = $(this);
            if(!self.multipostFBBusy) {
                self.multipostFBBusy = true;

                self.checkFBLogin(function() {
                    var checkedEvents = $(self.eventCheckerSelector + ":checked");
                    if(checkedEvents.length !== 0) {
                        self.miniIndicator.show().insertAfter(button);
                        self.eventsToPostCount = checkedEvents.length;

                        var ids = [];
                        $.each(checkedEvents, function() {
                            ids.push($(this).data("event-id"));
                        });

                        self.executeFBPosting(ids);
                    }
                    else {
                        self.multipostFBBusy = false;
                    }
                });
            }
        };

        self.onEventCheckboxChange = function() {
            var eventId = $(this).data("event-id");
            $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]")
                .not(this).
                removeAttr("checked");
        },

        self.executeFBPosting = function(eventIds) {
            if(eventIds.length !== 0) {
                var eventId = eventIds.shift();
                $.post(self.postFBUrl, {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId
                }, function(data) {
                    if(data.success) {
                        var message = self.createSuccessMessage();
                        self.successPostCount++;
                        message.html(self.successPostCount + " out of " + self.eventsToPostCount
                                              + " events posted to Facebook");

                        $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]").remove();
                    }
                    else {
                        var errorHtml = "Error while event posting: \"" + data.error + "\".";
                        if(data.event_link) {
                            errorHtml += " <a target='_blank' href='"+ data.event_link + "'>Link to the event</a>.";
                        }

                        var message = $("<div/>", {
                            "class": "alert-error",
                            "html": errorHtml
                        }).insertBefore($(self.postFBButtonSelector));
                    }

                    self.executeFBPosting(eventIds);
                }, 'json');
            }
            else {
                self.miniIndicator.hide();
                self.multipostFBBusy = false;

                var message = self.createSuccessMessage();
                message.html(self.successPostCount + " out of " + self.eventsToPostCount
                                              + " events posted to Facebook. "
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

        self.createSuccessMessage = function() {
            var message = $("[data-id=success_posting_message]");
            if(message.length === 0) {
                var message = $("<div/>", {
                    "class": "alert-success",
                    "data-id": "success_posting_message"
                }).insertBefore($(self.postFBButtonSelector));
            }

            return message;
        };

        self.init();
    };

    $(document).on("ready page:load", function(){
        new AccountService();
    });

})(jQuery, window, document);