;(function($, window, document, undefined) {

    'use strict';

    var SimilarEvents = function(){
        this.viewer = $(".similar-events-wrapper");
        this.itemsContainer = $("[data-id=similar_items_container]");
        this.controls = $(".similar-events-viewer-controls");
        this.next = $(".next", this.viewer);
        this.prev = $(".prev", this.viewer);
        this.pages = Math.ceil($("a", this.viewer).length/6);
        this.pageNo = $(".page-no", this.viewer);
        this.currentPage = 1;

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));

        $("#similar-events-total").html(this.pages);
        this.loadContent();
    };

    SimilarEvents.prototype = {
        _scroll: function(){
            $(this.content).animate({
                "top": -210*(this.currentPage-1) + "px"
            });
            this.pageNo.html(this.currentPage);
        },
        scrollToPage: function(page){
            if(page>0 && page<=this.pages){
                this.currentPage = page;
                this._scroll();
            }            
        },
        scrollNextPage: function(){
            this.scrollToPage(this.currentPage+1);
        },
        scrollPrevPage: function(){
            this.scrollToPage(this.currentPage-1);
        },
        loadContent: function() {
            var self = this;
            $.get(this.viewer.data("more-events-url"),
                function(data) {
                    if(data.success) {
                        self.itemsContainer.html(data.content);
                        self.content = $(".similar-events-ul", self.viewer);

                        if(data.count > 6) {
                            self.pages = Math.ceil(data.count/6);
                            $("#similar-events-total").html(self.pages);
                            self.controls.show();
                        }
                    }
                },
                'json'
            );
        }
    };

    window.SimilarEvents = SimilarEvents;

})(jQuery, window, document);