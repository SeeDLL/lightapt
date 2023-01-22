/*
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
 * 
 */


function onError(message) {
    $("#errorMessage").text(message);
    $("#centralModalDanger").modal("show");
};

// ----------------------------------------------------------------
// Get time
// ----------------------------------------------------------------

document.getElementById("get_time").addEventListener("click", getTime)
document.getElementById("sync_time").addEventListener("click", syncTime)
document.getElementById("reset_time").addEventListener("click", resetTime)

function getTime() {
    let now = new Date();
    let year = now.getFullYear();
    let month = now.getMonth() + 1;
    let day = now.getDate();
    let hour = now.getHours();
    let minute = now.getMinutes();
    let second = now.getSeconds();
    let time = year + ":" + month + ":" + day + "-" + hour + ":" + minute + ":" + second;
    console.log(time)
    $("#time").val(time)
    return time
}

function syncTime() {
    $.ajax({
        url: '/tools/api/time/' + getTime(),
        type: 'GET',
        async: true,
        processData: false,
        contentType: "application/json",
        success: function (data) {
            if (!data.error) {
                console.log(data.message);
                $("#time_info_message").text("Info: " + data.message);
                $("#time_info").removeAttr("hidden")
            }
            else {
                onError(data.error);
                $("#time_error_message").text("Error: " + data.error);
                $("#time_error").removeAttr("hidden")
            }
        },
        error: function () {
            onError("Failed to send request to server");
        }
    })
}

function resetTime() {
    $("#time").val("")
}

// ----------------------------------------------------------------
// Get location via client gps
// ----------------------------------------------------------------

document.getElementById('get_location').addEventListener('click', getLocation)
document.getElementById('sync_location').addEventListener('click', syncLocation)
document.getElementById('reset_location').addEventListener('click', resetLocation)

function getLocation() {
    let options = {
        enableHighAccuracy: true,
        maximumAge: 1000
    }
    // Web browsers support GPS option
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(onLocationSuccess, onLocationError, options);

    } else {
        onError("Web browser does not support GPS function");
    }
}

function syncLocation() {
    $.ajax({
        url: '/tools/api/location/' + $('#lon').val() + '/' + $('#lat').val(),
        type: 'GET',
        async: true,
        processData: false,
        contentType: "application/json",
        success: function (data) {
            if (!data.error) {
                console.log(data.message);
                $("#location_info_message").text("Info: " + data.message);
                $("#location_info").removeAttr("hidden")
            }
            else {
                onError(data.error);
                $("#location_error_message").text("Error: " + data.error);
                $("#location_error").removeAttr("hidden")
            }
        },
        error: function () {
            onError("Failed to send request to server");
        }
    })
}

function resetLocation() {
    $("#lon").val("");
    $("#lat").val("");
}

function onLocationSuccess(pos) {
    console.log("Lon:" + pos.coords.longitude + "Lat:" + pos.coords.latitude)
    $('#lon').val(pos.coords.longitude)
    $('#lat').val(pos.coords.latitude)
}

function onLocationError(error) {
    switch (error.code) {
        case 1:
            onError("Positioning function rejected")
            break;
        case 2:
            onError("Unable to obtain location information temporarily");
            break;
        case 3:
            onError("Get information timeout");
            break;
        case 4:
            onError("Unknown error");
            break;
    }
}


// ----------------------------------------------------------------
// Update the sotfwares
// ----------------------------------------------------------------



// ----------------------------------------------------------------
// Download the template file for astromical solver
// ----------------------------------------------------------------

$(() => {
    $("#solver").change(() => {
        console.log($('#solver').val());
        let solver = $('#solver').val();
        // If want to downlaad astrometry templates
        if (solver == "astrometry") {
            // First check whether the files had already downloaded
            $.ajax({
                url: '/tools/api/download/astrometry/already',
                type: 'GET',
                async: true,
                processData: false,
                contentType: "application/json",
                success: function (data) {
                    if (!data.error) {
                        console.log(data.message);
                    }
                    else {
                        onError(data.error);
                    }
                },
                error: function () {
                    onError("Failed to send request to server");
                }
            })
        }
        else {
            // Same step as astrometry
            $.ajax({
                url: '/tools/api/download/astap/already',
                type: 'GET',
                async: true,
                processData: false,
                contentType: "application/json",
                success: function (data) {
                    if (!data.error) {
                        console.log(data.message);
                    }
                    else {
                        onError(data.error);
                    }
                },
                error: function () {
                    onError("Failed to send request to server");
                }
            })
        }
    })
});


function LoadMap() {
    document.getElementById("map").firstChild.data = "";

    /* Set default to Warsaw, Poland */
    var lon = 30;
    var lat = 120;

    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([lon, lat]),
            zoom: 4
        })
    });

    var center = new ol.geom.Point(
        ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857')
    );

    iconFeature = new ol.Feature({
        geometry: center
    });

    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1.0],
            anchorXUnits: 'fraction',
            anchorYUnits: 'fraction',
            src: 'assets/img/marker.png'
        })
    });

    iconFeature.setStyle(iconStyle);

    var vectorSource = new ol.source.Vector({
        features: [iconFeature]
    });

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });

    map.addLayer(vectorLayer);
}

function UpdateMapPos(lon, lat) {
    iconFeature.setGeometry(new ol.geom.Point(ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857')));
    map.getView().animate({
        center: ol.proj.fromLonLat([lon, lat]),
        duration: 1000
    });
}

$(document).ready(function () {
    LoadMap();
    var url = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '');
    
    var socket = io(url);
    console.log(url)
    socket.on('connect', function() {
    });
    socket.on('gpspanel', function (gps) {
        $("#gpstime").html(gps.gpstime);
        $("#latitude").html(gps.latitude);
        $("#longitude").html(gps.longitude);
        $("#altitude").html(gps.altitude);
        $("#mode").html(gps.mode);
        $("#hdop").html(gps.hdop);
        $("#vdop").html(gps.vdop);

        if (gps.gpstime) {
            var d = new Date(gps.gpstime);
            var date = d.getUTCFullYear() + "-" + ("0" + (d.getUTCMonth() + 1)).substr(-2) + "-" + ("0" + d.getUTCDate()).substr(-2) + "T" + ("0" + d.getUTCHours()).substr(-2) + ":" + ("0" + d.getUTCMinutes()).substr(-2) + ":" + ("0" + d.getUTCSeconds()).substr(-2);
            $("#gtime").html(date);
        }

        if (gps.latitude && gps.longitude) {
            var lat = gps.latitude;
            var lon = gps.longitude;
            var lat_sign, lon_sign;

            UpdateMapPos(lon, lat);

            if (lat < 0) {
                lat_sign = '-';
            } else {
                lat_sign = '';
            }

            if (lon < 0) {
                lon_sign = '-';
            } else {
                lon_sign = '';
            }

            lat = Math.abs(lat);
            lon = Math.abs(lon);

            latdeg = parseInt(lat);
            latmin = parseInt((lat - latdeg) * 3600 / 60);
            latsec = ((lat - latdeg - latmin / 60) * 3600).toFixed(4);
            londeg = parseInt(lon);
            lonmin = parseInt((lon - londeg) * 3600 / 60);
            lonsec = ((lon - londeg - lonmin / 60) * 3600).toFixed(4);
            latrad = lat_sign + latdeg + ":" + ("0" + latmin).substr(-2) + ":" + ("0" + latsec).substr(-7);
            lonrad = lon_sign + londeg + ":" + ("0" + lonmin).substr(-2) + ":" + ("0" + lonsec).substr(-7);
            $("#lat").html(latrad);
            $("#lon").html(lonrad);
        }

        if (gps.sschart) {
            $("#sschart").attr("src", "data:image/png;base64," + gps.sschart);
        }

        if (gps.skymap) {
            $("#skymap").attr("src", "data:image/png;base64," + gps.skymap);
        }

        if (gps.satellites) {
            var satellites = "<table><tr><th colspan=5 align=left><h2>Visible Satellites<h2></th></tr><tr><th>PRN</th><th>Elevation</th><th>Azimuth</th><th>SS</th><th>Used</th></tr>";
            var used;
            for (const sat in gps.satellites) {
                if (gps.satellites[sat]['used']) {
                    used = 'Y';
                } else {
                    used = 'N';
                }
                satellites = satellites + "<tr align=right><td>" + gps.satellites[sat]['PRN'] + "</td><td>" + gps.satellites[sat]['el'] + "</td><td>" + gps.satellites[sat]['az'] + "</td><td>" + gps.satellites[sat]['ss'] + "</td><td>" + used + "</td></tr>";
            }
            satellites = satellites + "</table>";

            $("#sats").html(gps.satellites.length);
            $("#gpssats").html(satellites);
        }

        if (typeof (gps.mode) == 'number') {
            if (gps.mode == 3) {
                $("#gpsfix").html('3D');
                $("#gpsfix").removeClass("blink");
                $("#gpsfix_obtained").addClass("gpsfix_obtained");
            } else if (gps.mode == 2) {
                $("#gpsfix").html('2D');
                $("#gpsfix").removeClass("blink");
                $("#gpsfix_obtained").addClass("gpsfix_obtained");
            } else {
                $("#gpsfix").html('waiting...');
                $("#gpsfix").addClass("blink");
                $("#gpsfix_obtained").removeClass("gpsfix_obtained");
            }
        }
    });
});
