# XXXX work in progress...
#
import time
import os
import unittest
from contextlib import contextmanager

from mozproxy import get_playback
import mozinfo
import mozlog
import sys

from mozrunner import FirefoxRunner
from mozprofile import FirefoxProfile
from yttest.mario import YoutubePage
from marionette_driver.geckoinstance import apps


mozlog.commandline.setup_logging('mozproxy', {}, {'tbpl': sys.stdout})


here = os.path.dirname(__file__)
config = {}
config['app'] = 'firefox'
config['binary'] = ('/Users/tarek/Dev/gecko/mozilla-central-opt/'
                    'objdir-osx/dist/Nightly.app/Contents/MacOS/firefox')
config['platform'] = mozinfo.os
config['processor'] = mozinfo.processor
config['run_local'] = True
config['obj_path'] = '/tmp'
config['host'] = 'localhost'
config['playback_tool'] = 'mitmproxy'
config['custom_script'] = os.path.join(here, 'playback.py')

config['playback_recordings'] = 'wvpZZqmnNhg.playback'
#config['playback_pageset_manifest'] = 'mitmproxy-recordings-raptor-tp6.manifest'
config['playback_artifacts'] = 'https://ziade.org/wvpZZqmnNhg.tar.gz'

# XXX we should not have to set this
config['playback_binary_manifest'] = 'mitmproxy-rel-bin-osx.manifest'


@contextmanager
def youtube_video(video_id):
    proxy = get_playback(config)
    if proxy is None:
        raise Exception("Could not start Proxy")
    try:
        prefs = {"media.autoplay.default": 0}
        prefs["network.proxy.type"] = 1
        prefs["network.proxy.http"] = config['host']
        prefs["network.proxy.http_port"] = 8080
        prefs["network.proxy.ssl"] = config['host']
        prefs["network.proxy.ssl_port"] = 8080
        prefs["network.proxy.no_proxies_on"] = config['host']
        profile = FirefoxProfile(profile='/tmp/mozprof',
                                preferences=prefs,
                                addons=[])
        browser = apps['fxdesktop'].create(profile=profile,
                                app='fxdesktop',
                                bin=config['binary'],
                                app_args=[])
        browser.start()
    except Exception:
        proxy.stop()
        raise

    try:
        page = YoutubePage(video_id)
    except Exception:
        try:
            browser.close()
        finally:
            proxy.stop()
        raise

    try:
        yield page
    finally:
        try:
            page.close()
            browser.close()
        finally:
            proxy.stop()


S = """\
var video = document.getElementsByTagName("video")[0];
if (!video) {
  return "Can't find the video tag";
}

var vpq = video.getVideoPlaybackQuality();

# XXX add an event to check that the end of the video has been reached.
# XXX this event can also happen on the fake YT server side
# since the client sends a telemetry ping when this happens
return vpq;
"""


class YoutubeTest(unittest.TestCase):

    def test_stream(self):
        with youtube_video("wvpZZqmnNhg") as page:
            time.sleep(10)   # needs to wait, find out why XXX
            page.start_video()
            time.sleep(25)
            res = page.execute_script(S)
            # checking the video playback quality
            self.assertEqual(res['droppedVideoFrames'], 0)
            # XXX do the maths to see how much frames we were supposed to play
            self.assertEqual(res['totalVideoFrames'] > 700)


if __name__ == '__main__':
    unittest.main()
