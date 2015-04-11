/**
 * Created by rulkens on 03/04/15.
 */
function Eos(options){
    this.useSocket = options ? options.socket || false : false;
    if(this.useSocket){
        // initialize socket
        this.socket = new SockJS('http://' + window.location.host + '/api');
        this.socket.onopen = function() {
            console.log('Connected.');
            this.socket.send(JSON.stringify({ action: 'status', arguments: []}));
        }.bind(this);

        this.socket.onclose = function() {
            console.log('Disconnected.');
        }.bind(this);
    }
}

Eos.prototype = {
    api: function(action, arguments, cb){
        if(this.useSocket){
            var req = {action: action, arguments: arguments || [] };
            if(this.socket.readyState !== 0) this.socket.send(JSON.stringify(req));
            this.socket.onmessage = function(e) {
                //console.log('Received: ', e.data);
                if(cb) cb(e.data);
            }.bind(this);
        } else {
            var path = '/api/' + action;
            path += arguments ? '/' + arguments.join(',') : '';

            $.getJSON(path, function(ret){
                if(cb) cb(ret); // do a callback if you want it
            });
        }
    }
};