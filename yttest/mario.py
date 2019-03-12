"""
Drives the browser during the playback test.
"""
import os
from marionette_harness import Marionette

here = os.path.dirname(__file__)
js = os.path.join(here, "quality_test.js")
with open(js) as f:
    js_test = f.read()


class YoutubePage:
    def __init__(self, video_id):
        self.video_id = video_id
        self.client = Marionette(host="localhost", port=2828)
        self.url = "https://www.youtube.com/watch?v=%s" % self.video_id
        self.started = False

    def start_video(self):
        self.client.start_session()
        self.client.navigate(self.url)
        self.started = True

    def run_test(self):
        self.start_video()
        return self.execute_script(js_test)

    def execute_script(self, script, context=None):
        if context is None:
            context = self.client.CONTEXT_CONTENT
        with self.client.using_context(context):
            return self.client.execute_script(script, script_timeout=600*1000)

    def close(self):
        if self.started:
            self.client.close()
