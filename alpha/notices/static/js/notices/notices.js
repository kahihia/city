;(function($, window, document, undefined) {
    'use strict';

    var NoticesService = function() {
        var self = this;

        self.init = function() {
            self.readNoticeUrl = $("[data-type=hidden_elements] [data-id=read_notice_url]").val();

            self.closeButtonSelector = "[data-type=notice_close_button]";
            self.noticeItemSelector = "[data-type=notice_item]";

            $("body").on("click", self.closeButtonSelector, self.onCloseButtonClick);
        };

        self.onCloseButtonClick = function() {
            var button = $(this);
            var csrf = button.closest(self.noticeItemSelector).find("input[name=csrfmiddlewaretoken]").val();

            var params = {
                "csrfmiddlewaretoken": csrf,
                "notice_id": button.data("notice-id")
            };

            $.post(self.readNoticeUrl, params, function(data) {
                if(data.success) {
                    button.closest(self.noticeItemSelector).remove();
                }
            }, 'json');
        };

        self.init();
    };

    $(document).ready(function() {
        window.noticesService = new NoticesService();
    });
})(jQuery, window, document);