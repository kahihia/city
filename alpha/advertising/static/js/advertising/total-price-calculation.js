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
        this.bonus = $("#id_bonus_budget");
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
        changePaymentsVisibility: function(){
            var totalPrice = +this.budget.val();

            if(totalPrice) {
                $(".choose-payment-system .checkbox.paypal").removeClass("disabled");

            } else {
                $(".choose-payment-system .checkbox").addClass("disabled");
            }
        },
        calculateTotalPrice: function(){
            var that = this,
                totalPrice = +that.budget.val(),
                totalBudget;

            this.changePaymentsVisibility();

            _.forEach(this.taxes, function(tax){
                tax.calculatePrice(+that.budget.val());
                totalPrice += +tax.price();
            });

            totalBudget = totalPrice + parseFloat(that.bonus.val());

            $(".total-price-output").html(totalPrice.toFixed(2));
            $(".total-budget-output").html(totalBudget.toFixed(2));
        }
    };   


    window.TotalPriceCalculation = TotalPriceCalculation;

})(jQuery, window, document);