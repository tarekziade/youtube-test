# XXXX work in progress...
#
import os
from contextlib import contextmanager

from mozproxy import get_playback
import mozinfo
from mozprofile import FirefoxProfile
from yttest.mario import YoutubePage
from marionette_driver.geckoinstance import apps


here = os.path.dirname(__file__)
config = {}
config["app"] = "firefox"
config["binary"] = (
    "/Users/tarek/Dev/gecko/mozilla-central-opt/"
    "objdir-osx/dist/Nightly.app/Contents/MacOS/firefox"
)
config["platform"] = mozinfo.os
config["processor"] = mozinfo.processor
config["run_local"] = True
config["obj_path"] = "/tmp"
config["host"] = "localhost"
config["playback_tool"] = "mitmproxy"
config["custom_script"] = os.path.join(here, "playback.py")

# XXX we should use a generic name since the taball now
# contains several videos
config["playback_artifacts"] = "https://ziade.org/wvpZZqmnNhg.tar.gz"

# XXX we should not have to set this
config["playback_binary_manifest"] = "mitmproxy-rel-bin-osx.manifest"


@contextmanager
def youtube_video(video_id):
    config["playback_recordings"] = "%s.playback" % video_id
    config["playback_tool_args"] = [
    "--set", "upstream_cert=false",
    "-S", "/tmp/testing/mozproxy/%s.playback" % video_id,
    ]
    proxy = get_playback(config)
    if proxy is None:
        raise Exception("Could not start Proxy")
    try:
        prefs = {"media.autoplay.default": 0}
        prefs["browser.newtabpage.activity-stream.feeds.snippets"] = 0
        prefs["browser.newtabpage.activity-stream.disableSnippets"] = 1
        prefs["network.proxy.type"] = 1
        prefs["network.proxy.http"] = config["host"]
        prefs["network.proxy.http_port"] = 8080
        prefs["network.proxy.ssl"] = config["host"]
        prefs["network.proxy.ssl_port"] = 8080
        prefs["network.proxy.no_proxies_on"] = config["host"]
        profile = FirefoxProfile(profile="/tmp/mozprof", preferences=prefs, addons=[])
        browser = apps["fxdesktop"].create(
            profile=profile, app="fxdesktop", bin=config["binary"],
            app_args=["about:blank"]
        )
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
