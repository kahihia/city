;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingSetupPage(){
        this.initVenueAccountWidget();
        this.initActiveToWidget();
        this.initAdTypeSelection();
        this.initRegionSelection();
        this.initTotalPriceCalculation();
        this.initSwitchPaymemtModes();
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
            $(".advertising-types .checkbox input").each(function(){
                var ad_type_id = $(this).data("ad-type"),
                    checked = $(this).prop("checked");

                that.showOrHideUploadRow(
                    ad_type_id,
                    $("#id_advertising_type_" + ad_type_id).prop('checked')
                );
            });

            $(".advertising-types .radio input").on("click", function(){
                var ad_type_id = $(this).data("ad-type");
                $("#id_advertising_type_"+ad_type_id).prop('checked', true);

                that.showOrHideUploadRow(
                    ad_type_id,
                    $("#id_advertising_type_"+ad_type_id).prop('checked')
                );
            });

            $(".advertising-types .checkbox input").on("click", function(){
                var ad_type_id = $(this).data("ad-type"),
                    checked = $(this).prop("checked");

                if(checked){
                    if(!$("#advertising_type_"+ad_type_id+"_cpm").attr('checked') && !$("#advertising_type_"+ad_type_id+"_cpc").attr('checked')){
                        $("#advertising_type_"+ad_type_id+"_cpm").attr('checked', true);
                    }
                } else {
                    $("#advertising_type_"+ad_type_id+"_cpm").attr('checked', false);
                    $("#advertising_type_"+ad_type_id+"_cmc").attr('checked', false);
                }

                that.showOrHideUploadRow(
                    ad_type_id,
                    $("#id_advertising_type_"+ad_type_id).prop('checked')
                );
            });
        },
        showOrHideUploadRow: function(ad_type_id, checked){
            if(checked){
                $(".advertising-uploads [data-ad-type=" + ad_type_id + "]").show();
            } else {
                $(".advertising-uploads [data-ad-type=" + ad_type_id + "]").hide();
            }
        },
        initRegionSelection: function(){
            if($("#id_all_of_canada").prop("checked")){
                $(".advertising-territories .region").hide();
            }

            $("#id_all_of_canada").on("change", function(){
                if($(this).prop("checked")){
                    $(".advertising-territories .region").hide();
                } else {
                    $(".advertising-territories .region").show();
                }                
            });
        },
        initTotalPriceCalculation: function(){
            this.totalPriceCalculation = new TotalPriceCalculation();
        },
        initSwitchPaymemtModes: function(){
            if($("#id_budget_type").val()=="BONUS") {
                $('[data-tab-id="setup-bonus-budget"]').click();
            }
            $('[data-tab-id="setup-bonus-budget"]').on("click", function(){
                $("#id_budget_type").val("BONUS");
            });

            $('[data-tab-id="setup-real-budget"]').on("click", function(){
                $("#id_budget_type").val("REAL");
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