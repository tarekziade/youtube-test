"""
MITM Script used to collect media files when a YT video is played.
"""
import os
import re
import sys

from mitmproxy.tools.main import mitmdump
from yttest.util import print_itag, get_data_dir, log

_HERE = os.path.dirname(__file__)


def response(flow):
    if "googlevideo.com/videoplayback" in flow.request.url:
        itag = flow.request.query["itag"]
        log("Requested quality\n%s" % print_itag(itag))

        mime = flow.request.query["mime"].replace("/", "-")
        query_args = dict(flow.request.query)
        file_id = query_args["id"]
        file_range = query_args["range"]
        log("Writing %s:%s" % (file_id, file_range))
        # changing the host so the MITM recording file
        # does not rely on a specific YT server
        flow.request.host = "googlevideo.com"
        if len(flow.response.content) == 0:
            return
        path = "%s-%s-%s.%s" % (file_id, itag, file_range, mime)
        path = os.path.join(get_data_dir(), path)
        with open(path, "wb") as f:
            f.write(flow.response.content)


if __name__ == '__main__':
    script = _HERE + '/record.py'
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.argv[1:] = ['-w',  'data/%s.playback' % sys.argv[1],  '-s', script]
    sys.exit(mitmdump())
