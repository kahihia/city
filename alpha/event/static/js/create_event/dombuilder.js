(function($) {

    function dom(type, attrs, childs){
        var element = document.createElement(type),
            key;
        if(attrs){
            for(key in attrs){
                if(attrs.hasOwnProperty(key)){
                    if(key === "id" || key === "innerHTML" || key === "value" || key === "src" || key === "className"){
                        element[key] = attrs[key];
                    }else{
                        element.setAttribute(key, attrs[key]);
                    }
                }
            }
        }
        childs && childs.forEach(function(child){
           element.appendChild(child);
        });
        return element;
    };

    window.dom = dom;
})(jQuery);