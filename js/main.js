function plugins() {
  plugins = navigator.plugins;
  s = "";
  for(i=0; i<plugins.length; i++) {
    s += plugins[i].name + ",";
  }
  return s;
}

function addField(name, value) {
  var val = Cookies.get(name);
  if (typeof val == 'undefined') {
    Cookies.set(name, value);
  }
}

function getIP(json) {
  // called via JSONP
  addField('public_ip', json.ip);
}

function getUid() {
  return Math.random().toString(36).substring(2)
    + (new Date()).getTime().toString(36);
}

$(document).ready(function() {
  addField('device_id', getUid());
  addField('user_timezone', "UTC+"+new Date().toString().split('+')[1].split(' ')[0].substring(0,2)+":00"); //Intl.DateTimeFormat().resolvedOptions().timeZone);
  addField('client_screens', 'width=' + window.screen.width + '&height=' + window.screen.height + '&scaling-factor=1&colour-depth=' + window.screen.colorDepth);
  addField('client_window', 'width=' + window.innerWidth + '&height=' + window.innerHeight);
  addField('client_browser_plugins', plugins());
  addField('client_user_agent', navigator.userAgent);
  addField('client_do_not_track', navigator.doNotTrack == 1);
  addField('client-local-timestamp', new Date().toISOString())
});
