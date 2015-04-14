/**
 * Created by rulkens on 03/04/15.
 */
$(document).ready(function(){

    var eos = new Eos(
        { socket: true,
            onclose: function(){
                $('#statusLabel').removeClass('label-success').addClass('label-danger').text('disconnected');
            },
            onopen: function(){
                $('#statusLabel').removeClass('label-danger').addClass('label-success').text('connected');
            }
        });

    // generic eos api handler
    var mapValuesOnProperty = function(values, prop){
            return function(){
                var index = $(this).data('light');
                $(this)[prop](parseFloat(values[index]).toFixed(4));
            }
        },
        apiHandler = function(data){
            // update the view
            //console.log(data);
            showFeedback(data.status);
        },
        preventChange = false;
        showFeedback = function(values){
            // update all labels
            $('[data-label]').each(mapValuesOnProperty(values, 'text'));
            // update all sliders
            $('[data-slider]').each(function(){
                var index = $(this).data('light'),
                    curval = $(this).slider('getValue'),
                    newval = values[index];
                if(curval != newval){
                    $(this).slider('setValue', values[index]);
                }
            });

            // on/off toggle
            var toggleEl = $('#lightsToggle');
            var sum = values.reduce(function(val, item){
                return val + item;
            });
            if(sum > 0){
                 // stupid hack for the bootstrap toggle that always wants to
                if(!toggleEl.prop('checked')){
                    preventChange = true;
                    toggleEl.bootstrapToggle('on');
                }
            } else {
                if(toggleEl.prop('checked')){
                    preventChange = true;
                    toggleEl.bootstrapToggle('off');
                }
            }

            //
        },
        defaultApi = function(action, args){
            return eos.api(action, args, apiHandler);
        };


    // get the initial status
    defaultApi('status');

    // event handlers

    $('#lightsToggle').change(function(item){
        var action = $(this).prop('checked') ? 'allon' : 'alloff';
        if(!preventChange){
            defaultApi( action );
        }
        preventChange = false;
    });

    $('#stepSlider').slider().on('change', function(e){
        defaultApi('only', [$(this).slider('getValue'), 1]);
    });

    $('#intensitySlider').slider().on('change', function(e){
        defaultApi('all', [$(this).slider('getValue')]);
    });

    $('#gammaSlider').slider().on('change', function(e){
        defaultApi('gamma', [$(this).slider('getValue')]);
    });

    // for all the individual lights
    $('[data-slider]').slider();
    $('[data-slider]').on('change', function(e){
        var id = $(this).data('light');
        defaultApi('one', [id, $(this).slider('getValue')]);
    });



    // for programs

    // moving light

    var light = {
            pos: 0,
            size: 2.5,
            intensity: 0.5,
            falloff: 'quad'
        },
        lightArray = function(){
            return [light.pos, light.size, light.intensity, light.falloff]
        };

    $('#lightPosSlider').slider().on('change', function(e){
        light.pos = $(this).slider('getValue');
        defaultApi('light', lightArray());
    });

    $('#lightSizeSlider').slider().on('change', function(e){
        light.size = $(this).slider('getValue');
        defaultApi('light', lightArray());
    });

    $('#lightIntensitySlider').slider().on('change', function(e){
        light.intensity = $(this).slider('getValue');
        defaultApi('light', lightArray());
    });

    // GLOW
    $('#glowToggle').change(function(item){
        var arguments = [$(this).prop('checked') ? 'on' : 'off'];
        defaultApi('glow', arguments );
    });

});