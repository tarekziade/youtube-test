// this script is injected by marionette to collect metrics
var video = document.getElementsByTagName("video")[0];
if (!video) {
  return "Can't find the video tag";
}

async function test() {
  let promise = new Promise((resolve, reject) => {
    function videoEnded() {
      resolve(video.getVideoPlaybackQuality());
    }
    video.addEventListener("ended", videoEnded, true);
    // XXX not allowed, so we use autoplay
    // await video.play();
  });
  var vqp = await promise;
  return vqp;
}

return test();

