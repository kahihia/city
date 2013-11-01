;(function($, window, document, undefined) {
    'use strict';

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

    function TotalPriceCalculation(){
        var that = this;

        this.budget = $("#id_budget");
        this.bonus = $("#id_bonus");
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

        this.bonus.keyup(this.calculateTotalPrice.bind(this));
        this.bonus.on("change", this.calculateTotalPrice.bind(this));
    }

    TotalPriceCalculation.prototype = {
        checkBonus: function(){
            var bonus = +this.bonus.val(),
                budget = +this.budget.val();
            if(bonus>budget) {
                alert("Bonus can not be greater than budget");
                this.bonus.val("0.0");
            }
            if(bonus!=budget) {
                $(".choose-payment-system .checkbox.paypal").removeClass("disabled");
            } else {
                $(".choose-payment-system .checkbox").addClass("disabled");
            }
        },
        calculateTotalPrice: function(){
            this.checkBonus();

            var totalPrice = +this.budget.val() - parseFloat(this.bonus.val()),
                totalPriceWithTaxes = totalPrice;            

            _.forEach(this.taxes, function(tax){
                tax.calculatePrice(totalPrice);
                totalPriceWithTaxes += +tax.price();
            });            

            $(".total-price-output").html(totalPrice.toFixed(2));
            $(".total-price-with-taxes-output").html(totalPriceWithTaxes.toFixed(2));
        }
    };   


    window.TotalPriceCalculation = TotalPriceCalculation;

})(jQuery, window, document);