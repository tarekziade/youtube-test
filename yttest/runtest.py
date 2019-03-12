import sys
import time
import unittest

import mozlog
from yttest.support import youtube_video


mozlog.commandline.setup_logging("mozproxy", {}, {"tbpl": sys.stdout})


class YoutubeTest(unittest.TestCase):
    def test_stream(self):
        with youtube_video("wvpZZqmnNhg") as page:
            res = page.run_test()
            # checking the video playback quality
            self.assertEqual(res["droppedVideoFrames"], 0)
            # XXX do the maths to see how much frames we were supposed to play
            self.assertTrue(res["totalVideoFrames"] > 700)


if __name__ == "__main__":
    unittest.main()
