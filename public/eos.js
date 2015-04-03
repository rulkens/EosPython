/**
 * Created by rulkens on 03/04/15.
 */
function Eos(){

}

Eos.prototype = {
    api: function(action, arguments, cb){
        var path = '/api/' + action;
        path += arguments ? '/' + arguments.join(',') : '';

        $.getJSON(path, function(ret){
            console.log(ret);
            if(cb) cb(ret); // do a callback if you want it
        });
    }
};