/**
 * Created by rulkens on 03/04/15.
 */
function Eos(options){
    this.useSocket = options ? options.socket || false : false;
    if(this.useSocket){
        // initialize socket
        this.socket = io.connect('http://' + document.domain + ':' + (5153) + '/api');
        this.socket.on('result', function(result){
            console.log('socket result', result.result);
        });
    }
}

Eos.prototype = {
    api: function(action, arguments, cb){
        if(this.useSocket){
            this.socket.emit('action', { action: action, args: arguments }, function(result){
                console.log('result received from action', action, result);
            });
        } else {
            var path = '/api/' + action;
            path += arguments ? '/' + arguments.join(',') : '';

            $.getJSON(path, function(ret){
                console.log(ret);
                if(cb) cb(ret); // do a callback if you want it
            });
        }

    }
};