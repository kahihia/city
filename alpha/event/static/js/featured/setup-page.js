;(function($, window, document, undefined) {
    'use strict';

    function FeaturedSetupPage(){
        var start_date_input, end_date_input, days_to_display, bonus,
            that=this;

        start_date_input = $("#id_start_time");
        end_date_input = $("#id_end_time");
        days_to_display = $("#days_to_display");
        bonus = $("#id_bonus");

        $.datepicker.initialized = false;
        $(".dropdown.date").on("click", function(){
            $("input", this).datepicker("show");
        });

        start_date_input.datepicker({
            minDate: new Date(),
            onSelect: function(){
                that.calculate_days_to_display();
            }
        });

        end_date_input.datepicker({
            minDate: new Date(),
            onSelect: function(){
                that.calculate_days_to_display();
            }
        });

        days_to_display.on("change", this.calculate_end_date.bind(this));
        bonus.on("change", this.calculateTotalPrice.bind(this));

        this.start_date_input = start_date_input;
        this.end_date_input = end_date_input;
        this.days_to_display = days_to_display;
        this.bonus = bonus;

        this.initTotalPriceCalculation();
        this.initRegionsSelection();
        this.initSwitchPaymemtModes();

    }

    FeaturedSetupPage.prototype = {
        calculate_days_to_display: function(){
            var date1 = this.start_date_input.datepicker('getDate'),
                date2 = this.end_date_input.datepicker('getDate'),
                diff = 1, date, month, year;

            if(date1>date2) {
                year = date1.getFullYear();
                month = date1.getMonth();
                date = date1.getDate()+1;

                this.end_date_input.val(
                    $.datepicker.formatDate(
                        'mm/dd/yy',
                        new Date(year, month, date)
                    )
                );
                diff = 1;
            } 
            else if (date1 && date2) {
                diff = diff + Math.floor((date2.getTime() - date1.getTime()) / 86400000); // ms per day
            }

            this.days_to_display.val(diff);
            this.calculateTotalPrice();
        },
        calculate_end_date: function(){
            var start_date = this.start_date_input.datepicker('getDate'),
                date, month, year, days_to_display;

            days_to_display = +this.days_to_display.val();

            year = start_date.getFullYear();
            month = start_date.getMonth();
            date = start_date.getDate();

            this.end_date_input.val(
                $.datepicker.formatDate(
                    'mm/dd/yy',
                    new Date(year, month, date+days_to_display)
                )
            );
        },
        initTotalPriceCalculation: function(){
            var that = this;
            this.dayCost = $("#id_day_cost");
            this.taxes = [];

            this.taxRows = $(".tax-row");
            _.forEach(this.taxRows, function(row){
                that.taxes.push(
                    new TaxWidget(row)
                );
            });

            this.calculateTotalPrice();

            this.days_to_display.keyup(this.calculateTotalPrice.bind(this));
            this.days_to_display.on("change", this.calculateTotalPrice.bind(this));
        },
        checkBonus: function(costWithoutBonus){            
            if(costWithoutBonus>0){
                $(".choose-payment-system .checkbox.paypal").removeClass("disabled");
            } else {
                $(".choose-payment-system .checkbox").addClass("disabled");
            }
        },
        calculateTotalPrice: function(){
            var that = this,
                cost = +this.days_to_display.val() * + this.dayCost.val(),
                costWithoutBonus = cost - parseFloat(this.bonus.val()),
                totalPrice = costWithoutBonus;

            this.checkBonus(costWithoutBonus);

            if(costWithoutBonus<0) {
                alert("Bonus can not be greater than budget");
                this.bonus.val(cost);
                this.calculateTotalPrice()
            } else {
                _.forEach(this.taxes, function(tax){
                    tax.calculatePrice(+costWithoutBonus);
                    totalPrice += +tax.price();
                });

                $(".total-price-output").html(costWithoutBonus.toFixed(2));
                $(".total-price-with-taxes-output").html(totalPrice.toFixed(2));
            }
        },
        initRegionsSelection: function(){
            if($("#id_all_of_canada").prop("checked")){
                $(".choose-province-block .region").hide();
            }

            $("#id_all_of_canada").on("change", function(){
                if($(this).prop("checked")){
                    $(".choose-province-block .region").hide();
                } else {
                    $(".choose-province-block .region").show();
                }
            });
        },
        initSwitchPaymemtModes: function(){}
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
        window.featuredSetupPage = new FeaturedSetupPage();
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