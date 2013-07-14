;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingSetupPage(){
        this.initAdTypeSelection();
        this.initRegionSelection();
        this.initTotalPriceCalculation();
    }

    AdvertisingSetupPage.prototype = {
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
            var that = this;
            this.budget = $("#id_budget");
            this.taxes = [];

            this.taxRows = $(".tax-row");
            _.forEach(this.taxRows, function(row){
                that.taxes.push(
                    new TaxWidget(row)
                );
            });

            this.calculateTotalPrice();

            this.budget.keyup(this.calculateTotalPrice.bind(this));
            this.budget.on("change", this.calculateTotalPrice.bind(this));
        },
        calculateTotalPrice: function(){
            var that = this;
            var totalPrice = +that.budget.val();

            _.forEach(this.taxes, function(tax){
                tax.calculatePrice(+that.budget.val());
                totalPrice += +tax.price();
            });

            $(".total-price-output").html(totalPrice.toFixed(2));

        }
    };

    function TaxWidget(row){
        this.taxInput = $(".tax-input", row);
        this.taxPriceOutput = $(".tax-price", row);
    }

    TaxWidget.prototype = {
        calculatePrice: function(price){            
            this.taxPrice = this.tax() * price;
            this.taxPriceOutput.html(this.taxPrice.toFixed(2));
        },
        tax: function(){
            return +this.taxInput.val();
        },
        price: function(){
            return this.taxPrice.toFixed(2);
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