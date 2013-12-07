;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingSetupPage() {
        this.initVenueAccountWidget();
        this.initActiveToWidget();
        this.initAdTypeSelection();
        this.initRegionSelection();
        this.initUploads();
        this.initTotalPriceCalculation();
        this.initSwitchPaymemtModes();
        this.initSubmitButton();
        this.alignColumns();
    }

    AdvertisingSetupPage.prototype = {
        initVenueAccountWidget: function(){
            this.venueAccount = new VenueAccountOwnerWidget();
        },
        initActiveToWidget: function(){
            this.dateRange = new DateRange(
                document.getElementById("id_active_from"),
                document.getElementById("id_active_to"),
                true
            )
        },
        initAdTypeSelection: function(){
            var that=this;

            // Init rows
            $(".advertising-types input[type=checkbox]").each(function(){
                var ad_type_id = $(this).data("ad-type"),
                    checked = $(this).attr("checked");

                that.showOrHideUploadRow(ad_type_id, checked);
            });

            $(".advertising-types .ad-type-col .checkbox input").on("click", function() {
                var ad_type_id = $(this).data("ad-type"),
                    checked = $(this).attr('checked')?true:false;

                $("#id_advertising_type_"+ad_type_id).attr('checked', checked);

                that.showOrHideUploadRow(ad_type_id, checked);
            });
        },
        showOrHideUploadRow: function(ad_type_id, checked){
            if(checked){
                $(".advertising-uploads [data-ad-type=" + ad_type_id + "]").show();
            } else {
                $(".advertising-uploads [data-ad-type=" + ad_type_id + "]").hide();
            }

            this.alignColumns();
        },
        initRegionSelection: function(){
            var self = this;
            if($("#id_all_of_canada").attr("checked")){
                $(".advertising-territories .region").hide();
            }

            $("#id_all_of_canada").on("change", function(){
                if($(this).attr("checked")){
                    $(".advertising-territories .region").hide();
                } else {
                    $(".advertising-territories .region").show();
                }

                self.alignColumns();
            });
        },
        initUploads: function() {
            var fileInputSelector = ".advertising-uploads__file-field input";
            var haveFileApi = ( window.File && window.FileReader
                                && window.FileList && window.Blob ) ? true : false;

            $("body").on("change", fileInputSelector, function() {
                var fileName;
                var lbl = $(this).siblings("mark");
                var btn = $(this).siblings(".button");

                if( haveFileApi && this.files[ 0 ] )
                    fileName = this.files[ 0 ].name;
                else
                    fileName = $(this).val().replace( "C:\\fakepath\\", "" );

                if( ! fileName.length )
                    return;

                if( lbl.is( ":visible" ) ) {
                    lbl.text( fileName );
                    btn.text( "Choose File" );
                }else
                    btn.text( fileName );
            });


            $(fileInputSelector).change();

            $(".fancybox").fancybox();
        },
        initTotalPriceCalculation: function(){
            this.totalPriceCalculation = new TotalPriceCalculation();
        },
        initSwitchPaymemtModes: function(){
            
        },
        alignColumns: function() {
            var leftColumn = $(".advertising-form__details");
            var rightColumn = $(".advertising-form__budget");

            var leftHeight = leftColumn.outerHeight();
            var rightHeight = rightColumn.outerHeight();

            if(!this._initialRightHeight) {
                this._initialRightHeight = rightHeight;
            }

            if(leftHeight > this._initialRightHeight) {
                rightColumn.height(leftHeight - rightHeight + rightColumn.height());
            }
        },
        initSubmitButton: function() {
            $("body").on("click", ".advertising-form__submit", function(){
                $(this).closest("form").submit();
            });
        }
    };

    $(document).on("ready page:load", function(){
        var ballons;
        window.advertisingSetupPage = new AdvertisingSetupPage();
        $.balloon.defaults.classname = "hintbox";
        $.balloon.defaults.css = {};
        ballons = $(".balloon");
        $(ballons).each(function(){
            var content = $(this).siblings(".balloon-content");
            $(this).balloon({
                contents:content,
                position:"left bottom",
                tipSize: 0,
                offsetX:0,//$.browser.msie?0:25,
                offsetY:25,//$.browser.msie?25:0,
                showDuration: 500, hideDuration: 0,
                showAnimation: function(d) { this.fadeIn(d); }
            });
        });
    });

})(jQuery, window, document);