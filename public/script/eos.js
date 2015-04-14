/**
 * Created by rulkens on 03/04/15.
 */
/**
 * simple middleware for handling communication with the EOS through the HTTP REST API
 *
 * dependencies: jquery
 *
 * @type {{init: Function, api: Function}}
 */
var httpMiddleware = {
    init: function(){},
    api: function(action, args, cb){
        var path = '/api/' + action;
        path += args ? '/' + args.join(',') : '';

        $.getJSON(path, function(ret){
            if(cb) cb(ret); // do a callback if you want it
        });
    }
};

/**
 * middleware for handling communication with the EOS through the SockJS api
 *
 * dependencies: sockjs-client
 *
 * @type {{init: Function, api: Function}}
 */
var socketMiddleware = {
    init: function(){
        // initialize socket
        this.socket = new SockJS('http://' + window.location.host + '/api');
        this.socket.onopen = function() {
            console.log('[ws]', 'connected');
            //extra functionality for socket opening and closing events
            if(_.isFunction(this.onopen)) this.onopen();
            this.socket.send(JSON.stringify({ action: 'status', arguments: []}));
        }.bind(this);

        this.socket.onclose = function() {
            console.log('[ws]', 'disconnected');
            if(_.isFunction(this.onclose)) this.onclose();
        }.bind(this);
    },
    api: function(action, args, cb){
        var req = {action: action, arguments: args || [] };
        if(this.socket.readyState !== 0) this.socket.send(JSON.stringify(req));
        this.socket.onmessage = function(e) {
            //console.log('Received: ', e.data);
            if(cb) cb(e.data);
        }.bind(this);
    }
};

/**
 * main EOS object for communicating with the EOS python backend
 * @param options
 * - onopen: callback for when the connection to the eos is opened
 * - onclose: ballback when connection to eos is closed
 * @constructor
 */
function Eos(options){
    this.useSocket = options ? options.socket || false : false;
    _.defaults(this, options);

    this.handler = httpMiddleware;
    if(this.useSocket){
        this.handler = socketMiddleware;
    }
    this.handler.init.apply(this, options);
}

/**
 *
 * @type {{api: Function}}
 */
Eos.prototype = {
    /**
     * the main api function for communicating with the EOS lamp
     * @param action - the action to take
     * @param args - optional arguments for the action
     * @param cb - optional callback
     */
    api: function(action, args, cb){
        this.handler.api.apply(this, arguments);
    }
};