if (!Function.prototype.bind) {
  Function.prototype.bind = function (oThis) {
    if (typeof this !== "function") {
      // closest thing possible to the ECMAScript 5 internal IsCallable function
      throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
    }

    var aArgs = Array.prototype.slice.call(arguments, 1), 
        fToBind = this, 
        fNOP = function () {},
        fBound = function () {
          return fToBind.apply(this instanceof fNOP && oThis
                                 ? this
                                 : oThis,
                               aArgs.concat(Array.prototype.slice.call(arguments)));
        };

    fNOP.prototype = this.prototype;
    fBound.prototype = new fNOP();

    return fBound;
  };
}

if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    //Your implementation here. Might be worth looking at perf comparison at
    //http://blog.stevenlevithan.com/archives/faster-trim-javascript
    //
    //The most common one is perhaps this:
    return this.replace(/^\s+|\s+$/g, ''); 
  }
}