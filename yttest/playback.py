"""
MITM Script used to play back media files when a YT video is played.
"""
import os
import json
import sys
from collections import defaultdict
import datetime
import time
import shutil
import re

from mitmproxy import http
from mitmproxy.tools.main import mitmdump
from yttest.util import print_itag, get_data_dir, log

_HERE = os.path.dirname(__file__)

_HEADERS = {
    b"Last-Modified": b"Mon, 10 Dec 2018 19:39:24 GMT",
    b"Content-Type": b"video/webm",
    b"Date": b"Wed, 02 Jan 2019 15:14:06 GMT",
    b"Expires": b"Wed, 02 Jan 2019 15:14:06 GMT",
    b"Cache-Control": b"private, max-age=21292",
    b"Accept-Ranges": b"bytes",
    b"Content-Length": b"173448",
    b"Connection": b"keep-alive",
    b"Alt-Svc": b'quic=":443"; ma=2592000; v="44,43,39,35"',
    b"Access-Control-Allow-Origin": b"https://www.youtube.com",
    b"Access-Control-Allow-Credentials": b"true",
    b"Timing-Allow-Origin": b"https://www.youtube.com",
    b"Access-Control-Expose-Headers": (
        b"Client-Protocol, Content-Length, "
        b"Content-Type, X-Bandwidth-Est, "
        b"X-Bandwidth-Est2, X-Bandwidth-Est3, "
        b"X-Bandwidth-App-Limited, "
        b"X-Bandwidth-Est-App-Limited, "
        b"X-Bandwidth-Est-Comp, X-Bandwidth-Avg, "
        b"X-Head-Time-Millis, X-Head-Time-Sec, "
        b"X-Head-Seqnum, X-Response-Itag, "
        b"X-Restrict-Formats-Hint, "
        b"X-Sequence-Num, X-Segment-Lmt, "
        b"X-Walltime-Ms"
    ),
    b"X-Restrict-Formats-Hint": b"None",
    b"X-Content-Type-Options": b"nosniff",
    b"Server": b"gvs 1.0",
}


def full_build(file_id):
    chunks = defaultdict(list)
    for f in os.listdir(get_data_dir()):
        if not f.startswith(file_id):
            continue
        extension = f.split(".")[-1]
        full_name = "full-%s.%s" % (file_id, extension)
        full_name = os.path.join(get_data_dir(), full_name)
        if os.path.exists(full_name):
            continue
        frange = f.split(".")[0].split("-")[-3:]
        itag, start, end = frange[0], int(frange[1]), int(frange[2])
        f = os.path.join(get_data_dir(), f)
        with open(f, "rb") as content:
            chunks[itag, extension].append((start, end, content.read()))

    for (itag, extension), chunk in chunks.items():
        full_name = "full-%s-%s.%s" % (file_id, itag, extension)
        full_name = os.path.join(get_data_dir(), full_name)
        if os.path.exists(full_name):
            continue
        chunk.sort()
        buffer = b""
        for start, end, data in chunk:
            buffer += data
        with open(full_name, "wb") as f:
            f.write(buffer)


def get_cached_data(request):
    query_args = dict(request.query)
    mime = query_args["mime"]
    file_id = query_args["id"]
    file_range = query_args["range"]
    itag = query_args["itag"]
    log("Request File %s - %s" % (file_id, mime))
    log("Requested range %s" % file_range)
    log("Requested quality\n%s" % print_itag(itag))
    frange = file_range.split("-")
    range_start, range_end = int(frange[0]), int(frange[1])
    fn = "full-%s-%s.%s" % (file_id, itag, mime.replace("/", "-"))
    fn = os.path.join(get_data_dir(), fn)
    if not os.path.exists(fn):
        raise Exception("no file at %s" % fn)
    with open(fn, "rb") as f:
        data = f.read()
    data = data[range_start:range_end] + b"'"
    headers = dict(_HEADERS)
    headers[b"Content-Type"] = bytes(mime, "utf8")
    headers[b"Content-Length"] = bytes(str(len(data)), "utf8")
    return headers.items(), data


def OK(flow, code=204):
    flow.error = None
    flow.response = http.HTTPResponse(b"HTTP/1.1", code, b"OK", {}, b"")


def request(flow):
    if flow.request.url.startswith("https://www.youtube.com/ptracking"):
        OK(flow)
        return
    if flow.request.url.startswith("https://www.youtube.com/api/stats/playback"):
        OK(flow)
        return
    if flow.request.url.startswith("https://www.youtube.com/api/stats/watchtime"):
        OK(flow)
        return
    if flow.request.method == "POST":
        OK(flow)
        return
    if "googlevideo.com/videoplayback" in flow.request.url:
        query_args = dict(flow.request.query)
        file_id = query_args["id"]
        full_build(file_id)
        file_range = query_args["range"]
        headers, data = get_cached_data(flow.request)
        headers = list(headers)
        flow.error = None
        flow.response = http.HTTPResponse(b"HTTP/1.1", 200, b"OK", headers, data)
        now = datetime.datetime.now()
        then = now - datetime.timedelta(hours=1)
        flow.response.timestamp_start = time.mktime(then.timetuple())
        flow.response.refresh()
        log("SENT FILE %s IN CACHE - range %s" % (file_id, file_range))


if __name__ == '__main__':
    script = _HERE + '/playback.py'
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.argv[1:] = ['-S',  'data/%s.playback' % sys.argv[1],  '-s', script,
                    '-k', '--server-replay-nopop']
    sys.exit(mitmdump())
