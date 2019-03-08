# XXXX work in progress...
#
import os
import unittest
from contextlib import contextmanager

from mozproxy import get_playback
import mozinfo
import mozlog
import sys
from mozrunner import FirefoxRunner
from mozprofile import FirefoxProfile


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
def open_youtube_video(video_id):
    url = "https://www.youtube.com/watch?v=%s" % video_id
    proxy = get_playback(config)
    if proxy is None:
        raise Exception("Could not start Proxy")
    try:
        env = os.environ.copy()
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
        browser = FirefoxRunner(profile=profile,
                                binary=config['binary'],
                                cmdargs=[url],
                                env=env)

        browser.start()
    except Exception:
        proxy.stop()
        raise

    try:
        yield
    finally:
        browser.wait(timeout=20)
        proxy.stop()


class YoutubeTest(unittest.TestCase):

    def test_stream(self):
        with open_youtube_video("wvpZZqmnNhg"):
            # inject and run the test using marionette here
            assert True


if __name__ == '__main__':
    unittest.main()