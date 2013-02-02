function Validator(form) {
    var messages = new Array();
    var fields = new Array();
    var labels = new Array();

    var allLabels = form.getElementsByTagName("label");
    for (var c = 0;c<allLabels.length;c++) {
        var label = allLabels[c];
        labels[label.htmlFor] = label.innerHTML;
    }

    this.validateEmail = function(field) {
        alert('E-mail de validation: ' + field);
    };

    this.verify = function() {
        if (this.isEmpty()) return true;
        alert(this.getFullErrorMessage());
        return false;
    };
    this.isEmpty = function() {
        return this.getSize() <= 0;
    };

    this.getSize = function() {
        return messages.length + fields.length;
    };

    this.requiredField = function(field) {
        if (field.value.length <= 0) {
            this.addField(field);
        }
    };

    this.requiredPassCheck= function(field1, field2){
        if(field1.value!=field2.value){
            this.addMessage('\tMot de passe erroné');
        }
    };

    this.addLabel = function(name,label) {
        labels[name] = label;
    };
    this.addMessage = function(message) {
        messages[messages.length] = message;
    };

    this.addField = function(field) {
        fields[fields.length] = field;
    };

    this.clear = new function() {
        messages = new Array();
        fields = new Array();
    };

    this.getFullErrorMessage = function() {
        var error = "";
        var c;

        if ((messages.length == 1) && (this.getSize() == 1)) {
            error = messages[0];
        } else {
            if (fields.length > 0) {
                error = error + "Les champs suivants sont obligatoires:";
                for (c = 0; c < fields.length; c++) {
                    var field = fields[c];
                    error = error + "\n\t* ";
                    var label = labels[field.id];
                    if ((label == null) || (label.length <= 0)) label = field.name;
                    error = error + label;
                }
            }
            if (messages.length > 0) {
                if (error.length > 0) error = error + "\n";
                for (c = 0; c < messages.length; c++) {
                    var msg = messages[c];
                    error = error + "\n";
                    error = error + msg;
                }
            }
        }
        return error;
    };
}
