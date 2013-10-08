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

            $("body").on("click", self.postFBButtonSelector, self.onFBPostButtonClick);
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

        self.executeFBPosting = function(eventIds) {
            if(eventIds.length !== 0) {
                var eventId = eventIds.shift();
                var eventNum = self.eventsToPostCount - eventIds.length;
                $.post(self.postFBUrl, {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId
                }, function(data) {
                    if(data.success) {
                        var message = $("<div/>", {
                            "class": "alert-success",
                            "html": eventNum + " out of " + self.eventsToPostCount + " events posted successfully"
                        }).insertBefore($(self.postFBButtonSelector));

                        $(self.eventCheckerSelector + "[data-event-id=" + eventId + "]").remove();
                        self.executeFBPosting(eventIds);
                    }
                    else {
                        var message = $("<div/>", {
                            "class": "alert-error",
                            "html": "Error while posting " + eventNum + " out of "
                                        + self.eventsToPostCount + " event: " + data.error
                        }).insertBefore($(self.postFBButtonSelector));
                    }

                    window.setTimeout(function() {
                        message.remove();
                    }, 4000);
                }, 'json');
            }
            else {
                self.miniIndicator.hide();
                self.multipostFBBusy = false;
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

        self.init();
    };

    $(document).on("ready page:load", function(){
        new AccountService();
    });

})(jQuery, window, document);