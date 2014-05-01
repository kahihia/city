;(function($, window, document, undefined) {
    'use strict';

    var ChangeVenueOwnerPage = function() {
        this.initUserInputs();
        this.initTransferButton();
    }

    ChangeVenueOwnerPage.prototype = {
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
            this.venueContainer = $("[data-id=venue_container]");
            this.csrfToken = $("input[name=csrfmiddlewaretoken]").val();
            this.transferUrl = this.venueContainer.data("transfer-url");

            $("body").on("click", "[data-id=transfer_button]", {obj: this}, this.onTransferButtonClick);
            $("body").on("click", "[data-id=select_all_button]", this.onSelectAllButtonClick);
        },

        onTransferButtonClick: function(event) {
            var self = event.data.obj;

            self.venuesToTransferCount = 0;
            var targetId = $("[data-id=target_id]").val();

            if(!self.transferBusy && targetId) {
                self.transferBusy = true;

                var checkedVenues = $("[data-type=venue_check]:checked");
                if(checkedVenues.length !== 0) {
                    self.venuesToTransferCount = checkedVenues.length;

                    var ids = [];
                    $.each(checkedVenues, function() {
                        ids.push($(this).data("venue-id"));
                    });

                    self.executeTransferring(ids, targetId);
                }
                else {
                    self.transferBusy = false;
                }
            }
        },

        onSelectAllButtonClick: function() {
            var checked = parseInt($(this).attr("data-checked"));
            if(!checked) {
                $(this).attr("data-checked", 1);
                $("[data-type=venue_check]").prop("checked", true);
            }
            else {
                $(this).attr("data-checked", 0);
                $("[data-type=venue_check]").prop("checked", false);
            }
        },

        executeTransferring: function(venueIds, targetId) {
            var self = this;

            $.post(self.transferUrl, {
                "csrfmiddlewaretoken": self.csrfToken,
                "venue_ids": venueIds,
                "owner_id": targetId
            }, function(data) {

                $.each(venueIds, function() {
                    $("[data-type=venue_check][data-venue-id=" + this + "]").remove();
                });

                var message = $("<div/>", {
                    "class": "alert-success",
                    "data-id": "success_transfer_message"
                });

                self.venueContainer.prepend(message);

                message.html(data.result + " out of " + self.venuesToTransferCount
                                              + " venues transferred. "
                                              + "Operation complete!");
                self.transferBusy = false;
            }, 'json');
        }
    }        

    $(document).ready(function(){
        new ChangeVenueOwnerPage();
    });

})(jQuery, window, document);