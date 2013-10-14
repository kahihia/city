;(function($, window, document, undefined) {
    'use strict';

    var ChangeEventOwnerPage = function() {
        this.initUserInputs();
        this.initTransferButton();
    }

    ChangeEventOwnerPage.prototype = {
        initUserInputs: function() {
            $(".user-input").each(function(index, input){
                $(input).select2({
                    placeholder: "User name",
                    minimumInputLength: 2,
                    ajax: {
                        url: $(input).data("ajax-url"),
                        dataType: "json",
                        data: function (term, page) {
                            return { "search": term };
                        },
                        results: function (data) {
                            return {results: data};
                        }
                    },
                    formatResult: function(data) {
                        return "<span>" + data.name + "</span>";
                    },
                    formatSelection: function(data) {
                        return "<span>" + data.name + "</span>";
                    }
                });

                var initDataElement = $("[data-id=" + $(input).attr("name") + "_init_data" + "]");
                if(initDataElement.length !== 0) {
                    $(input).select2("data", {"id": initDataElement.data("user-id"),
                                              "name": initDataElement.data("user-name")});
                }
            });
        },

        initTransferButton: function() {
            this.eventContainer = $("[data-id=event_container]");
            this.csrfToken = $("input[name=csrfmiddlewaretoken]").val();
            this.transferUrl = this.eventContainer.data("transfer-url");

            $("body").on("click", "[data-id=transfer_button]", {obj: this}, this.onTransferButtonClick);
        },

        onTransferButtonClick: function(event) {
            var self = event.data.obj;

            self.eventsToTransferCount = 0;
            self.successTransferCount = 0;
            var targetId = $("[data-id=target_id]").val();

            if(!self.transferBusy && targetId) {
                self.transferBusy = true;

                var checkedEvents = $("[data-type=event_check]:checked");
                if(checkedEvents.length !== 0) {
                    self.eventsToTransferCount = checkedEvents.length;

                    var ids = [];
                    $.each(checkedEvents, function() {
                        ids.push($(this).data("event-id"));
                    });

                    self.executeTransferring(ids, targetId);
                }
                else {
                    self.transferBusy = false;
                }
            }
        },

        executeTransferring: function(eventIds, targetId) {
            var self = this;

            if(eventIds.length !== 0) {
                var eventId = eventIds.shift();
                $.post(self.transferUrl, {
                    "csrfmiddlewaretoken": self.csrfToken,
                    "event_id": eventId,
                    "owner_id": targetId
                }, function(data) {
                    if(data.success) {
                        var message = $("[data-id=success_transfer_message]");
                        if(message.length === 0) {
                            var message = $("<div/>", {
                                "class": "alert-success",
                                "data-id": "success_transfer_message"
                            });

                            self.eventContainer.prepend(message);
                        }

                        self.successTransferCount++;
                        message.html(self.successTransferCount + " out of " + self.eventsToTransferCount
                                              + " events transferred.");

                        $("[data-type=event_check][data-event-id=" + eventId + "]").remove();
                    }

                    self.executeTransferring(eventIds, targetId);
                }, 'json');
            }
            else {
                self.transferBusy = false;

                var message = $("[data-id=success_transfer_message]");
                if(message.length === 0) {
                    var message = $("<div/>", {
                        "class": "alert-success",
                        "data-id": "success_transfer_message"
                    });

                    self.eventContainer.prepend(message);
                }

                message.html(self.successTransferCount + " out of " + self.eventsToTransferCount
                                              + " events transferred. "
                                              + "Operation complete!");
            }
        }
    }        

    $(document).ready(function(){
        new ChangeEventOwnerPage();
    });

})(jQuery, window, document);