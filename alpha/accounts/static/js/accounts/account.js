;(function($, window, document, undefined) {
    'use strict';

    var AccountService = function() {
        var self = this;

        self.init = function() {
            self.clearGraphUrl = $("[data-type=hidden_elements] [data-id=clear_graph_url]").val();
            self.multipostFBUrl = $("[data-type=hidden_elements] [data-id=multipost_to_facebook]").val();

            self.csrfToken = $("[data-type=hidden_elements] input[name=csrfmiddlewaretoken]").val();
            self.eventCheckerSelector = "[data-type=event_check]";
            self.miniIndicator = $("[data-id=mini_indicator]");
            self.multipostFBBusy = false;

            $("body").on("click", "[data-id=fb_post_button]", self.onFBPostButtonClick);
        }

        self.onFBPostButtonClick = function() {
            var button = $(this);
            if(!self.multipostFBBusy) {
                self.multipostFBBusy = true;

                self.checkFBLogin(function() {
                    var checkedEvents = $(self.eventCheckerSelector + ":checked");
                    if(checkedEvents.length !== 0) {
                        button.append(self.miniIndicator.show());

                        var ids = [];
                        $.each(checkedEvents, function() {
                            ids.push($(this).data("event-id"));
                        });

                        $.post(self.multipostFBUrl, {
                            "csrfmiddlewaretoken": self.csrfToken,
                            "event_ids": ids
                        }, function(data) {
                            if(data.success) {
                                self.miniIndicator.hide();

                                var message = $("<div/>", {
                                    "class": "alert-success",
                                    "html": data.posted.length + " out of " + ids.length + " events posted successfully"
                                }).insertAfter(button);

                                $.each(data.posted, function() {
                                    $(self.eventCheckerSelector + "[data-event-id=" + this + "]").remove();
                                });

                                window.setTimeout(function() {
                                    message.remove();
                                }, 4000);

                                self.multipostFBBusy = false;
                            }
                        }, 'json');
                    }
                });
            }
        };

        self.checkFBLogin = function(successCallback) {
            if(typeof(FB) === "undefined") {
                alert("Facebook library isn't ready yet. Please, wait.");
                return;
            }

            FB.getLoginStatus(function(response) {
                if (response.status === 'connected') {
                    successCallback();
                } else {
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
                }
            });
        };

        self.init();
    };

    $(document).on("ready page:load", function(){
        new AccountService();
    });

})(jQuery, window, document);