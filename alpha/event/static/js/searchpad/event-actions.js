;(function($, window, document, undefined) {
    'use strict';

    function EventActions(eventDetailsBlock){
        var that=this;
        this.eventElement = eventDetailsBlock;

        this.inTheLoop = new InTheLoop(eventDetailsBlock);
        this.remindMe = new RemindMe(eventDetailsBlock);
    }

    EventActions.prototype = {
        
    };

    window.EventActions = EventActions;

})(jQuery, window, document);