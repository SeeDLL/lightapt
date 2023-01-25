/*
 * Copyright(c) 2022-2023 Max Qian
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

// ----------------------------------------------------------------
// Basic Interface
// ----------------------------------------------------------------

/**
 * Print Error Messages In Screen 
 * @param {string} _err
 */
function onError(_err) {
    $("#errorMessage").text(_err);
    $("#centralModalDanger").modal("show");
}

/**
 * Hide message modal
 */
function onErrorHide() {
    $("#centralModalDanger").modal("hide");
}

/**
 * Double check for better safety
 */
function onWarning() {
    $("#centralModalDanger").modal("show");
}

/**
 * Hide the warning message
 */
function onWarningHide() {
    $("#centralModalDanger").modal("hide");
}

/**
 * Print Normal Messages
 * @param {string} _info
 */
function onInfo(_info) {
    $("#infoModalMessage").text(_info);
    $("#infoModalGeneric").modal("show");
}

/**
 * Hide the modal message at a proper time
 */
function onInfoHide() {
    setTimeout(function () {
        $("#infoModalGeneric").modal("hide");
    }, 600);
}

/**
 * Tiny single line logging system
 * @param {string} msg 
 */
function logText(msg) {
    $("#generalLogText").text(msg)
}

// ----------------------------------------------------------------
// Event handlers on loading finished
// ----------------------------------------------------------------

var ready = callback => {
    "loading" != document.readyState ? callback() : document.addEventListener("DOMContentLoaded", callback)
};

ready(() => {
    // We need to run this function to check if the server is ready started.
    getStatus();
    // Bind events with server_command
    document.getElementById("server_command").addEventListener("click", toggle_server)
    // Bind events with client_command , NOTE : This client does not mean INDI client,
    // this is connecting to another standalone server as a better INDI interface
    // If you are using ASCOM as your server , just avoid this .
    // Before the INDI server is started , we can not connect to client
    $('#client_command').addClass("disabled");
    document.getElementById("client_command").addEventListener("click", toggle_client)
});

// ----------------------------------------------------------------
// Device Hub Interface
// ----------------------------------------------------------------

/**
 * Start or stop the server and all of the drivers that started by this server
 */
function toggle_server() {
    var status = $.trim($("#server_command").text());
    if (status == "启动" || status == "start" || status == "Start") {
        onInfo("连接中,请稍后...")
        $.ajax({
            type: 'POST',
            url: "/devices/api/start",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                camera: $("#camera").val(),
                telescope: $("#telescope").val(),
                focuser: $("#focuser").val(),
                filterwheel: $("#filterwheel").val(),
                solver: $("solver").val(),
                guider: $("#guider").val(),
                plugins: $("#plugins").val()
            }),
            success: function () {
                onInfoHide();
                getStatus();
            },
            error: function () {
                onInfoHide();
                onError("启动设备失败");
            }
        });
    } else {
        $.ajax({
            type: 'GET',
            url: "/devices/api/stop",
            success: function () {
                getStatus();
            },
            error: function () {
                onError("停止设备失败")
            }
        });
    }
};

/**
 * Get the status of the server 
 */
function getStatus() {
    $.getJSON("/devices/api/status", function (data) {
        if (data.status == "True")
            getActiveDrivers();
        else {
            $("#server_command").html("<i class='fas fa-light-switch-on'></i> 启动");
            $("#server_notify").html("<p class='alert alert-info'>服务器空闲中</p>");

            $("#server_command").removeClass('btn-outlinedanger');
            $("#server_command").addClass('btn-outline-primary');
        }
    });
};

/**
 * Get all of the active drivers and modifiers html whit a success symbol
 */
function getActiveDrivers() {
    $.getJSON("/devices/api/drivers", function (data) {
        $("#server_command").html("<i class='fas fa-close'></i> 停止");
        $("#server_command").addClass('btn-outline-info');
        $("#server_command").removeClass('btn-outline-danger');

        $("#server_notify").html("<p class='alert alert-info'>设备启动成功！</p>");

        $("#client_command").removeClass("disabled");
    })
};

// ----------------------------------------------------------------
// Websocket Connection Options
// ----------------------------------------------------------------

var websocket;
var is_connected = false;

/**
 * Toggles the client connection.
 * This function is used to set up a websocket connection with the server.
 * The server is built-in and not INDI server at all.
 */
function toggle_client() {
    var status = $.trim($("#client_command").text());
    if (status == "连接" || status == "start" || status == "Start") {
        // Create a new websocket connection
        websocket = new WebSocket("ws://localhost:5000")
        websocket.onopen = function (event) { on_open(event) }
        websocket.onclose = function (event) { on_close(event) }
        websocket.onmessage = function (event) { on_message(event) }
        websocket.onerror = function (event) { on_error(event) }
    } else {
        websocket.close()
    }
};

/**
 * Wesocket On open event
 * @param {*} event 
 */
function on_open(event) {
    is_connected = true;
    $("#client_command").html("<i class='fas fa-close'></i> 断连");
    $("#client_notify").html("<p class='alert alert-info'>与服务器建立连接</p>");
    SendRemoteDashboardSetup();
}

/**
 * Websocket On close event
 * @param {*} event 
 */
function on_close(event) {
    is_connected = false;
    $("#client_command").html("<i class='fas fa-link'></i> 连接");
    $("#client_notify").html("<p class='alert alert-warning'>暂无连接</p>");
}

/**
 * Websocket On message event
 * When a message is received , first we will check if the message format is JSON
 * and if it is correct , the parser_json() will be called to parse the message
 * @param {*} event 
 */
function on_message(event) {
    try {
        var message = JSON.parse(event.data.replace(/\bNaN\b/g, "null"))
    }
    catch (e) {
        console.error("Not a valid JSON message : " + e)
    }
    "RemotePolling" !== message.event && parser_json(message)
}

/**
 * Websocket On error event
 * @param {*} event 
 */
function on_error(event) {
    console.debug("websocket error")
    onError("Websocket连接错误")
}

/**
 * Send message to the websocket server
 * @param {string} message
 */
function on_send(message) {
    // send message to server
    console.debug("send message : " + message)
    if (is_connected) {
        websocket.send(message + "\r\n")
    }
}

// ----------------------------------------------------------------
// Websocket event handlers
// ----------------------------------------------------------------

function SendRemoteDashboardSetup() {
    // Send setup command to remote server
    let request = {
        event: "RemoteDashboardSetup",
        params: {}
    }
    on_send(JSON.stringify(request))
}


// ----------------------------------------------------------------
// Image Viewer
// ----------------------------------------------------------------

window.onload = function () {
    'use strict';

    var Viewer = window.Viewer;
    var console = window.console || { log: function () { } };
    var pictures = document.querySelector('.docs-pictures');
    var toggles = document.querySelector('.docs-toggles');
    var buttons = document.querySelector('.docs-buttons');
    var options = {
        // inline: true,
        url: 'data-original',
        ready: function (e) {
        },
        show: function (e) {
        },
        shown: function (e) {
        },
        hide: function (e) {
        },
        hidden: function (e) {
        },
        view: function (e) {
        },
        viewed: function (e) {
        },
        move: function (e) {
        },
        moved: function (e) {
        },
        rotate: function (e) {
        },
        rotated: function (e) {
        },
        scale: function (e) {
        },
        scaled: function (e) {
        },
        zoom: function (e) {
        },
        zoomed: function (e) {
        },
        play: function (e) {
        },
        stop: function (e) {
        }
    };
    var viewer = new Viewer(pictures, options);

    function toggleButtons(mode) {
        var targets;
        var target;
        var length;
        var i;

        if (/modal|inline|none/.test(mode)) {
            targets = buttons.querySelectorAll('button[data-enable]');

            for (i = 0, length = targets.length; i < length; i++) {
                target = targets[i];
                target.disabled = true;

                if (String(target.getAttribute('data-enable')).indexOf(mode) > -1) {
                    target.disabled = false;
                }
            }
        }
    }
};

// ----------------------------------------------------------------
// Guiding Line Render
// ----------------------------------------------------------------

$(function () {

    var RAData = [];
    var DECData = [];

    var GuidingLineData = {
        datasets: [
            {
                label: 'RA',
                backgroundColor: 'rgba(60,141,188,0.9)',
                borderColor: 'rgba(0,0,255,0.8)',
                pointRadius: false,
                pointColor: '#3b8bba',
                pointStrokeColor: 'rgba(60,141,188,1)',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(60,141,188,1)',
                data: RAData
            },
            {
                label: 'DEC',
                backgroundColor: 'rgba(255,0 ,0, 1)',
                borderColor: 'rgba(255, 0, 0, 0.8)',
                pointRadius: true,
                pointColor: 'rgba(210, 214, 222, 1)',
                pointStrokeColor: '#c1c7d1',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(220,220,220,1)',
                data: DECData
            },
        ]
    }

    var GuidingLineOptions = {
        maintainAspectRatio: false,
        responsive: true,
        legend: {
            display: true
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display: true,
                }
            }],
            yAxes: [{
                gridLines: {
                    display: true,
                }
            }]
        }
    }


    var guiding_line_canvas = $('#guiding_line').get(0).getContext('2d')
    var guiding_line_options = $.extend(true, {}, GuidingLineOptions)
    var guiding_line_data = $.extend(true, {}, GuidingLineData)
    guiding_line_data.datasets[0].fill = false;
    guiding_line_data.datasets[1].fill = false;
    guiding_line_options.datasetFill = false

    var guiding_chart = new Chart(guiding_line_canvas, {
        type: 'line',
        data: guiding_line_data,
        options: guiding_line_options
    })

    //触发事件
    var active = {
        offset: function (othis) {
            var type = othis.data('type')
                , text = othis.text();

            layer.open({
                type: 1
                , offset: type //具体配置参考：https://www.layuiweb.com/doc/modules/layer.html#offset
                , id: 'layerDemo' + type //防止重复弹出
                , content: `<div class="card card-primary">
                                <div class="card-header">
                                    <h3 class="card-title">
                                        <i class="fas fa-star"></i>
                                        导星曲线
                                    </h3>
                                    <div class="card-tools">
                                        <button type="button" class="btn btn-tool" id="clear_guiding_line">
                                            <i class="fas fa-paint-brush"></i>
                                        </button>
                                        <button type="button" class="btn btn-tool" id="refresh_guiding_line">
                                            <i class="fas fa-redo"></i>
                                        </button>
                                        <button type="button" class="btn btn-tool btn-sm" data-card-widget="collapse">
                                            <i class="fas fa-minus"></i>
                                        </button>
                                        <button type="button" class="btn btn-tool btn-sm layui-layer-close">
                                            <i class="fas fa-close"></i>
                                        </button>
                                        
                                    </div>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-12">
                                            <div class="chart"><canvas id="guiding_line_"
                                                    style="min-height: 150px; height: 150px; max-height: 250px; max-width: 100%;"></canvas></div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-6">
                                            <div class="form-group">
                                                <label for="x_axis_">X轴</label>
                                                <select class="form-control selectpicker" id="x_axis_"
                                                    style="width: 100%;">
                                                    <option value="50">50</option>
                                                    <option value="100" selected="selected">100</option>
                                                    <option value="150">150</option>
                                                    <option value="200">200</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-sm-6">
                                            <div class="form-group">
                                                <label for="y_axis_">Y轴</label>
                                                <select class="form-control selectpicker" id="y_axis_" style="width: 100%;">
                                                    <option value="1">1</option>
                                                    <option value="2">2</option>
                                                    <option value="4" selected="selected">4</option>
                                                    <option value="8">8</option>
                                                    <option value="16">16</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            `
                , shade: 0 //不显示遮罩
                , yes: function () {
                    layer.closeAll();
                }
            });

            var guiding_line_canvas_ = $('#guiding_line_').get(0).getContext('2d')
            var guiding_line_options_ = $.extend(true, {}, GuidingLineOptions)
            var guiding_line_data_ = $.extend(true, {}, GuidingLineData)
            guiding_line_data_.datasets[0].fill = false;
            guiding_line_data_.datasets[1].fill = false;
            guiding_line_options_.datasetFill = false

            var guiding_chart_ = new Chart(guiding_line_canvas_, {
                type: 'line',
                data: guiding_line_data,
                options: guiding_line_options
            })
        }
    };

    $('.layui-btn').on('click', function () {
        var othis = $(this), method = othis.data('method');
        active[method] ? active[method].call(this, othis) : '';
    });


    //多窗口模式 - esc 键
    $(document).on('keyup', function (e) {
        if (e.keyCode === 27) {
            layer.close(layer.escIndex ? layer.escIndex[0] : 0);
        }
    });
});

// ----------------------------------------------------------------
// HFD line Renders
// ----------------------------------------------------------------

$(function () {

    var hfdData = []
    var hfdLineData = {
        datasets: [
            {
                label: 'HFD',
                yAxisID: 'hfd',
                backgroundColor: 'rgba(60,141,188,0.9)',
                borderColor: 'rgba(0,255,0,0.8)',
                pointRadius: false,
                pointColor: '#3b8bba',
                pointStrokeColor: 'rgba(60,141,188,1)',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(60,141,188,1)',
                data: hfdData
            }
        ]
    }

    var hfdLineOptions = {
        maintainAspectRatio: false,
        responsive: true,
        legend: {
            display: true
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display: true,
                }
            }],
            yAxes: [{
                gridLines: {
                    display: true,
                }
            }]
        }
    }

    var hfd_line_canvas = $('#hfd_line').get(0).getContext('2d')
    var hfd_line_options = $.extend(true, {}, hfdLineOptions)
    var hfd_line_data = $.extend(true, {}, hfdLineData)
    hfd_line_data.datasets[0].fill = false;
    hfd_line_options.datasetFill = false

    var hfd_chart = new Chart(hfd_line_canvas, {
        type: 'line',
        data: hfd_line_data,
        options: hfd_line_options
    })
});

// ----------------------------------------------------------------
// Cooling Line Render
// ----------------------------------------------------------------

$(function () {

    var TempData = [];
    var PowerData = [];

    var coolingLineData = {
        datasets: [
            {
                label: '制冷温度',
                yAxisID: 'temperature',
                backgroundColor: 'rgba(60,141,188,0.9)',
                borderColor: 'rgba(0,0,255,0.8)',
                pointRadius: false,
                pointColor: '#3b8bba',
                pointStrokeColor: 'rgba(60,141,188,1)',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(60,141,188,1)',
                data: TempData
            },
            {
                label: '制冷功率',
                yAxisID: 'power',
                backgroundColor: 'rgba(255,0 ,0, 1)',
                borderColor: 'rgba(255, 0, 0, 0.8)',
                pointRadius: true,
                pointColor: 'rgba(210, 214, 222, 1)',
                pointStrokeColor: '#c1c7d1',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(220,220,220,1)',
                data: PowerData
            },
        ]
    }

    var coolingLineOptions = {
        maintainAspectRatio: false,
        responsive: true,
        legend: {
            display: true
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display: true,
                }
            }],
            yAxes: [{
                gridLines: {
                    display: true,
                },
            }, {
                type: 'value',
                name: 'power',
                display: true
            }
            ]

        }
    }

    var cooling_line_canvas = $('#cooling_line').get(0).getContext('2d')
    var cooling_line_options = $.extend(true, {}, coolingLineOptions)
    var cooling_line_data = $.extend(true, {}, coolingLineData)
    cooling_line_data.datasets[0].fill = false;
    cooling_line_data.datasets[1].fill = false;
    cooling_line_options.datasetFill = false

    var cooling_chart = new Chart(cooling_line_canvas, {
        type: 'line',
        data: cooling_line_data,
        options: cooling_line_options
    })
});

// ----------------------------------------------------------------
// Sky map render
// ----------------------------------------------------------------

var config = {

    width: screen.width / 2.3,     // Default width, 0 = full parent width; height is determined by projection
    projection: "aitoff",  // Map projection used: airy, aitoff, armadillo, august, azimuthalEqualArea, azimuthalEquidistant, baker, berghaus, boggs, bonne, bromley, collignon, craig, craster, cylindricalEqualArea, cylindricalStereographic, eckert1, eckert2, eckert3, eckert4, eckert5, eckert6, eisenlohr, equirectangular, fahey, foucaut, ginzburg4, ginzburg5, ginzburg6, ginzburg8, ginzburg9, gringorten, hammer, hatano, healpix, hill, homolosine, kavrayskiy7, lagrange, larrivee, laskowski, loximuthal, mercator, miller, mollweide, mtFlatPolarParabolic, mtFlatPolarQuartic, mtFlatPolarSinusoidal, naturalEarth, nellHammer, orthographic, patterson, polyconic, rectangularPolyconic, robinson, sinusoidal, stereographic, times, twoPointEquidistant, vanDerGrinten, vanDerGrinten2, vanDerGrinten3, vanDerGrinten4, wagner4, wagner6, wagner7, wiechel, winkel3
    projectionRatio: null, // Optional override for default projection ratio
    transform: "equatorial", // Coordinate transformation: equatorial (default), ecliptic, galactic, supergalactic
    center: null,       // Initial center coordinates in equatorial transformation [hours, degrees, degrees],
    // otherwise [degrees, degrees, degrees], 3rd parameter is orientation, null = default center
    orientationfixed: true,  // Keep orientation angle the same as center[2]
    background: { fill: "#fff", stroke: "#000", opacity: 1, width: 1 }, // Background style
    adaptable: true,    // Sizes are increased with higher zoom-levels
    interactive: true,  // Enable zooming and rotation with mousewheel and dragging
    disableAnimations: false, // Disable all animations
    form: false,        // Display settings form
    location: false,    // Display location settings
    controls: true,     // Display zoom controls
    lang: "",           // Language for names, so far only for constellations: de: german, es: spanish
    // Default:en or empty string for english
    container: "celestial-map",   // ID of parent element, e.g. div
    datapath: "/static/json/stardata/",  // Path/URL to data files, empty = subfolder 'data'
    stars: {
        show: true,    // Show stars
        limit: 6,      // Show only stars brighter than limit magnitude
        colors: false,  // Show stars in spectral colors, if not use "color"
        style: { fill: "#000", opacity: 1 }, // Default style for stars
        names: false,   // Show star names (Bayer, Flamsteed, Variable star, Gliese, whichever applies first)
        proper: true, // Show proper name (if present)
        desig: false,  // Show all names, including Draper and Hipparcos
        namelimit: 2.5,  // Show only names for stars brighter than namelimit
        namestyle: { fill: "#ddddbb", font: "11px Georgia, Times, 'Times Roman', serif", align: "left", baseline: "top" },
        propernamestyle: { fill: "#ddddbb", font: "11px Georgia, Times, 'Times Roman', serif", align: "right", baseline: "bottom" },
        propernamelimit: 1.5,  // Show proper names for stars brighter than propernamelimit
        size: 7,       // Maximum size (radius) of star circle in pixels
        exponent: -0.28, // Scale exponent for star size, larger = more linear
        data: 'stars.6.json' // Data source for stellar data
        //data: 'stars.8.json' // Alternative deeper data source for stellar data
    },
    dsos: {
        show: true,    // Show Deep Space Objects
        limit: 6,      // Show only DSOs brighter than limit magnitude
        names: true,   // Show DSO names
        desig: true,   // Show short DSO names
        namelimit: 4,  // Show only names for DSOs brighter than namelimit
        namestyle: { fill: "#cccccc", font: "11px Helvetica, Arial, serif", align: "left", baseline: "top" },
        size: null,    // Optional seperate scale size for DSOs, null = stars.size
        exponent: 1.4, // Scale exponent for DSO size, larger = more non-linear
        data: 'dsos.bright.json',  // Data source for DSOs
        //data: 'dsos.6.json'  // Alternative broader data source for DSOs
        //data: 'dsos.14.json' // Alternative deeper data source for DSOs
        symbols: {  //DSO symbol styles
            gg: { shape: "circle", fill: "#ff0000" },                                 // Galaxy cluster
            g: { shape: "ellipse", fill: "#ff0000" },                                // Generic galaxy
            s: { shape: "ellipse", fill: "#ff0000" },                                // Spiral galaxy
            s0: { shape: "ellipse", fill: "#ff0000" },                                // Lenticular galaxy
            sd: { shape: "ellipse", fill: "#ff0000" },                                // Dwarf galaxy
            e: { shape: "ellipse", fill: "#ff0000" },                                // Elliptical galaxy
            i: { shape: "ellipse", fill: "#ff0000" },                                // Irregular galaxy
            oc: { shape: "circle", fill: "#ffcc00", stroke: "#ffcc00", width: 1.5 },  // Open cluster
            gc: { shape: "circle", fill: "#ff9900" },                                 // Globular cluster
            en: { shape: "square", fill: "#ff00cc" },                                 // Emission nebula
            bn: { shape: "square", fill: "#ff00cc", stroke: "#ff00cc", width: 2 },    // Generic bright nebula
            sfr: { shape: "square", fill: "#cc00ff", stroke: "#cc00ff", width: 2 },    // Star forming region
            rn: { shape: "square", fill: "#00ooff" },                                 // Reflection nebula
            pn: { shape: "diamond", fill: "#00cccc" },                                // Planetary nebula
            snr: { shape: "diamond", fill: "#ff00cc" },                                // Supernova remnant
            dn: { shape: "square", fill: "#999999", stroke: "#999999", width: 2 },    // Dark nebula grey
            pos: { shape: "marker", fill: "#cccccc", stroke: "#cccccc", width: 1.5 }   // Generic marker
        }
    },
    constellations: {
        show: true,    // Show constellations
        names: true,   // Show constellation names
        desig: true,   // Show short constellation names (3 letter designations)
        namestyle: {
            fill: "#cccc99", align: "center", baseline: "middle", opacity: 0.8,
            font: ["bold 14px Helvetica, Arial, sans-serif",  // Different fonts for brighter &
                "bold 12px Helvetica, Arial, sans-serif",  // sdarker constellations
                "bold 11px Helvetica, Arial, sans-serif"]
        },
        lines: true,   // Show constellation lines
        linestyle: { stroke: "#cccccc", width: 1, opacity: 0.6 },
        bounds: false,  // Show constellation boundaries
        boundstyle: { stroke: "#cccc00", width: 0.5, opacity: 0.8, dash: [2, 4] }
    },
    mw: {
        show: true,    // Show Milky Way as filled polygons
        style: { fill: "#996", opacity: 0.1 }
    },
    lines: {
        graticule: {
            show: true, stroke: "#cccccc", width: 0.6, opacity: 0.8,      // Show graticule lines
            // grid values: "outline", "center", or [lat,...] specific position
            lon: { pos: ["center"], fill: "#eee", font: "10px Helvetica, Arial, sans-serif" },
            // grid values: "outline", "center", or [lon,...] specific position
            lat: { pos: ["center"], fill: "#eee", font: "10px Helvetica, Arial, sans-serif" }
        },
        equatorial: { show: true, stroke: "#aaaaaa", width: 1.3, opacity: 0.7 },    // Show equatorial plane
        ecliptic: { show: true, stroke: "#66cc66", width: 1.3, opacity: 0.7 },      // Show ecliptic plane
        galactic: { show: false, stroke: "#cc6666", width: 1.3, opacity: 0.7 },     // Show galactic plane
        supergalactic: { show: false, stroke: "#cc66cc", width: 1.3, opacity: 0.7 } // Show supergalactic plane
    }
};

// Asterisms canvas style properties for lines and text
var pointStyle = {
    stroke: "rgba(255, 0, 204, 1)",
    fill: "rgba(255, 0, 204, 0.15)"
},
    textStyle = {
        fill: "rgba(255, 0, 204, 1)",
        font: "normal bold 15px Helvetica, Arial, sans-serif",
        align: "left",
        baseline: "bottom"
    };

// JSON structure of the object to be displayed, in this case
// the Summer Triangle between Vega, Deneb and Altair
var jsonSnr = {
    "type": "FeatureCollection",
    // this is an array, add as many objects as you want
    "features": [
        {
            "type": "Feature",
            "id": "SomeDesignator",
            "properties": {
                // Name
                "name": "Some Name",
                // Size in arcminutes
                "dim": 10
            }, "geometry": {
                // the line object as an array of point coordinates
                "type": "Point",
                "coordinates": [-80.7653, 38.7837]
            }
        }
    ]
};

// Closest distance between labels
var PROXIMITY_LIMIT = 20;

Celestial.add({
    type: "json",
    file: "/static/json/stardata/stars.6.json",

    callback: function (error, json) {

        if (error) return console.warn(error);
        // Load the geoJSON file and transform to correct coordinate system, if necessary
        var dsos = Celestial.getData(json, config.transform);

        // Add to celestiasl objects container in d3
        Celestial.container.selectAll(".snrs")
            .data(dsos.features.filter(function (d) {
                return d.properties.type === 'snr'
            }))
            .enter().append("path")
            .attr("class", "snr");
        // Trigger redraw to display changes
        Celestial.redraw();
    },

    redraw: function () {

        var m = Celestial.metrics(), // Get the current map size in pixels
            // empty quadtree, will be used for proximity check
            quadtree = d3.geom.quadtree().extent([[-1, -1], [m.width + 1, m.height + 1]])([]);

        // Select the added objects by class name as given previously
        Celestial.container.selectAll(".snr").each(function (d) {
            // If point is visible (this doesn't work automatically for points)
            if (Celestial.clip(d.geometry.coordinates)) {
                // get point coordinates
                var pt = Celestial.mapProjection(d.geometry.coordinates);
                // object radius in pixel, could be varable depending on e.g. magnitude
                var r = Math.pow(parseInt(d.properties.dim) * 0.25, 0.5);

                // draw on canvas
                // Set object styles
                Celestial.setStyle(pointStyle);
                // Start the drawing path
                Celestial.context.beginPath();
                // Thats a circle in html5 canvas
                Celestial.context.arc(pt[0], pt[1], r, 0, 2 * Math.PI);
                // Finish the drawing path
                Celestial.context.closePath();
                // Draw a line along the path with the prevoiusly set stroke color and line width
                Celestial.context.stroke();
                // Fill the object path with the prevoiusly set fill color
                Celestial.context.fill();

                // Find nearest neighbor
                var nearest = quadtree.find(pt);

                // If neigbor exists, check distance limit
                if (!nearest || distance(nearest, pt) > PROXIMITY_LIMIT) {
                    // Nothing too close, add it and go on
                    quadtree.add(pt)
                    // Set text styles
                    Celestial.setTextStyle(textStyle);
                    // and draw text on canvas with offset
                    Celestial.context.fillText(d.properties.name, pt[0] + r + 2, pt[1] + r + 2);
                }
            }
        });
    }
});

// Simple point distance function
function distance(p1, p2) {
    var d1 = p2[0] - p1[0],
        d2 = p2[1] - p1[1];
    return Math.sqrt(d1 * d1 + d2 * d2);
}

Celestial.display(config);
