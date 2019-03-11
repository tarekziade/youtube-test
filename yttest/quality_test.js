
var video = document.getElementsByTagName("video")[0];
if (!video) {
  return "Can't find the video tag";
}

var vpq = video.getVideoPlaybackQuality();

// XXX add an event to check that the end of the video has been reached.
// XXX this event can also happen on the fake YT server side
// since the client sends a telemetry ping when this happens
return vpq;
