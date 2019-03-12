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
            self.assertTrue(res["droppedVideoFrames"] < 744. * 0.1)
            self.assertEqual(res["totalVideoFrames"], 744)

        with youtube_video("BZP1rYjoBgI") as page:
            res = page.run_test()
            # checking the video playback quality
            self.assertTrue(res["droppedVideoFrames"] < 886. * 0.1)
            self.assertEqual(res["totalVideoFrames"], 886)


if __name__ == "__main__":
    unittest.main()
