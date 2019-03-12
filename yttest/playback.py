"""
MITM Script used to play back media files when a YT video is played.

This is a self-contained script that should not import anything else
except modules from the standard library and mitmproxy modules.
"""
import os
import sys
from collections import defaultdict
import datetime
import time
import re


itags = {
    5: {
        "Extension": "flv",
        "Resolution": "240p",
        "VideoEncoding": "Sorenson H.283",
        "AudioEncoding": "mp3",
        "Itag": 5,
        "AudioBitrate": 64,
    },
    6: {
        "Extension": "flv",
        "Resolution": "270p",
        "VideoEncoding": "Sorenson H.263",
        "AudioEncoding": "mp3",
        "Itag": 6,
        "AudioBitrate": 64,
    },
    13: {
        "Extension": "3gp",
        "Resolution": "",
        "VideoEncoding": "MPEG-4 Visual",
        "AudioEncoding": "aac",
        "Itag": 13,
        "AudioBitrate": 0,
    },
    17: {
        "Extension": "3gp",
        "Resolution": "144p",
        "VideoEncoding": "MPEG-4 Visual",
        "AudioEncoding": "aac",
        "Itag": 17,
        "AudioBitrate": 24,
    },
    18: {
        "Extension": "mp4",
        "Resolution": "360p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 18,
        "AudioBitrate": 96,
    },
    22: {
        "Extension": "mp4",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 22,
        "AudioBitrate": 192,
    },
    34: {
        "Extension": "flv",
        "Resolution": "480p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 34,
        "AudioBitrate": 128,
    },
    35: {
        "Extension": "flv",
        "Resolution": "360p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 35,
        "AudioBitrate": 128,
    },
    36: {
        "Extension": "3gp",
        "Resolution": "240p",
        "VideoEncoding": "MPEG-4 Visual",
        "AudioEncoding": "aac",
        "Itag": 36,
        "AudioBitrate": 36,
    },
    37: {
        "Extension": "mp4",
        "Resolution": "1080p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 37,
        "AudioBitrate": 192,
    },
    38: {
        "Extension": "mp4",
        "Resolution": "3072p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 38,
        "AudioBitrate": 192,
    },
    43: {
        "Extension": "webm",
        "Resolution": "360p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 43,
        "AudioBitrate": 128,
    },
    44: {
        "Extension": "webm",
        "Resolution": "480p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 44,
        "AudioBitrate": 128,
    },
    45: {
        "Extension": "webm",
        "Resolution": "720p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 45,
        "AudioBitrate": 192,
    },
    46: {
        "Extension": "webm",
        "Resolution": "1080p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 46,
        "AudioBitrate": 192,
    },
    82: {
        "Extension": "mp4",
        "Resolution": "360p",
        "VideoEncoding": "H.264",
        "Itag": 82,
        "AudioBitrate": 96,
    },
    83: {
        "Extension": "mp4",
        "Resolution": "240p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 83,
        "AudioBitrate": 96,
    },
    84: {
        "Extension": "mp4",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 84,
        "AudioBitrate": 192,
    },
    85: {
        "Extension": "mp4",
        "Resolution": "1080p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 85,
        "AudioBitrate": 192,
    },
    100: {
        "Extension": "webm",
        "Resolution": "360p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 100,
        "AudioBitrate": 128,
    },
    101: {
        "Extension": "webm",
        "Resolution": "360p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 101,
        "AudioBitrate": 192,
    },
    102: {
        "Extension": "webm",
        "Resolution": "720p",
        "VideoEncoding": "VP8",
        "AudioEncoding": "vorbis",
        "Itag": 102,
        "AudioBitrate": 192,
    },
    133: {
        "Extension": "mp4",
        "Resolution": "240p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 133,
        "AudioBitrate": 0,
    },
    134: {
        "Extension": "mp4",
        "Resolution": "360p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 134,
        "AudioBitrate": 0,
    },
    135: {
        "Extension": "mp4",
        "Resolution": "480p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 135,
        "AudioBitrate": 0,
    },
    136: {
        "Extension": "mp4",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 136,
        "AudioBitrate": 0,
    },
    137: {
        "Extension": "mp4",
        "Resolution": "1080p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 137,
        "AudioBitrate": 0,
    },
    138: {
        "Extension": "mp4",
        "Resolution": "2160p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 138,
        "AudioBitrate": 0,
    },
    160: {
        "Extension": "mp4",
        "Resolution": "144p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 160,
        "AudioBitrate": 0,
    },
    242: {
        "Extension": "webm",
        "Resolution": "240p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 242,
        "AudioBitrate": 0,
    },
    243: {
        "Extension": "webm",
        "Resolution": "360p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 243,
        "AudioBitrate": 0,
    },
    244: {
        "Extension": "webm",
        "Resolution": "480p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 244,
        "AudioBitrate": 0,
    },
    247: {
        "Extension": "webm",
        "Resolution": "720p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 247,
        "AudioBitrate": 0,
    },
    248: {
        "Extension": "webm",
        "Resolution": "1080p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 248,
        "AudioBitrate": 9,
    },
    264: {
        "Extension": "mp4",
        "Resolution": "1440p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 264,
        "AudioBitrate": 0,
    },
    266: {
        "Extension": "mp4",
        "Resolution": "2160p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 266,
        "AudioBitrate": 0,
    },
    271: {
        "Extension": "webm",
        "Resolution": "1440p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 271,
        "AudioBitrate": 0,
    },
    272: {
        "Extension": "webm",
        "Resolution": "2160p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 272,
        "AudioBitrate": 0,
    },
    278: {
        "Extension": "webm",
        "Resolution": "144p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 278,
        "AudioBitrate": 0,
    },
    298: {
        "Extension": "mp4",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 298,
        "AudioBitrate": 0,
    },
    299: {
        "Extension": "mp4",
        "Resolution": "1080p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "",
        "Itag": 299,
        "AudioBitrate": 0,
    },
    302: {
        "Extension": "webm",
        "Resolution": "720p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 302,
        "AudioBitrate": 0,
    },
    303: {
        "Extension": "webm",
        "Resolution": "1080p",
        "VideoEncoding": "VP9",
        "AudioEncoding": "",
        "Itag": 303,
        "AudioBitrate": 0,
    },
    139: {
        "Extension": "mp4",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "aac",
        "Itag": 139,
        "AudioBitrate": 48,
    },
    140: {
        "Extension": "mp4",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "aac",
        "Itag": 140,
        "AudioBitrate": 128,
    },
    141: {
        "Extension": "mp4",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "aac",
        "Itag": 141,
        "AudioBitrate": 256,
    },
    171: {
        "Extension": "webm",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "vorbis",
        "Itag": 171,
        "AudioBitrate": 128,
    },
    172: {
        "Extension": "webm",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "vorbis",
        "Itag": 172,
        "AudioBitrate": 192,
    },
    249: {
        "Extension": "webm",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "opus",
        "Itag": 249,
        "AudioBitrate": 50,
    },
    250: {
        "Extension": "webm",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "opus",
        "Itag": 250,
        "AudioBitrate": 70,
    },
    251: {
        "Extension": "webm",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "opus",
        "Itag": 251,
        "AudioBitrate": 160,
    },
    92: {
        "Extension": "ts",
        "Resolution": "240p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 92,
        "AudioBitrate": 48,
    },
    93: {
        "Extension": "ts",
        "Resolution": "480p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 93,
        "AudioBitrate": 128,
    },
    94: {
        "Extension": "ts",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 94,
        "AudioBitrate": 128,
    },
    95: {
        "Extension": "ts",
        "Resolution": "1080p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 95,
        "AudioBitrate": 256,
    },
    96: {
        "Extension": "ts",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 96,
        "AudioBitrate": 256,
    },
    120: {
        "Extension": "flv",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 120,
        "AudioBitrate": 128,
    },
    127: {
        "Extension": "ts",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "aac",
        "Itag": 127,
        "AudioBitrate": 96,
    },
    128: {
        "Extension": "ts",
        "Resolution": "",
        "VideoEncoding": "",
        "AudioEncoding": "aac",
        "Itag": 128,
        "AudioBitrate": 96,
    },
    132: {
        "Extension": "ts",
        "Resolution": "240p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 132,
        "AudioBitrate": 48,
    },
    151: {
        "Extension": "ts",
        "Resolution": "720p",
        "VideoEncoding": "H.264",
        "AudioEncoding": "aac",
        "Itag": 151,
        "AudioBitrate": 24,
    },
}


def print_itag(itag):
    itag_info = ["  %s: %s" % (k, v) for k, v in get_itag_info(itag).items()]
    return "\n".join(itag_info)


def get_itag_info(itag):
    return itags[int(itag)]


def log(msg):
    print(msg)


_HERE = os.path.dirname(__file__)
if "MOZPROXY_DIR" in os.environ:
    _DEFAULT_DATA_DIR = os.environ["MOZPROXY_DIR"]
else:
    _DEFAULT_DATA_DIR = os.path.join(_HERE, "..", "data")

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


def full_build(file_id, datadir=_DEFAULT_DATA_DIR):
    chunks = defaultdict(list)
    for f in os.listdir(datadir):
        if not f.startswith(file_id):
            continue
        extension = f.split(".")[-1]
        full_name = "full-%s.%s" % (file_id, extension)
        full_name = os.path.join(datadir, full_name)
        if os.path.exists(full_name):
            continue
        frange = f.split(".")[0].split("-")[-3:]
        itag, start, end = frange[0], int(frange[1]), int(frange[2])
        f = os.path.join(datadir, f)
        with open(f, "rb") as content:
            chunks[itag, extension].append((start, end, content.read()))

    for (itag, extension), chunk in chunks.items():
        full_name = "full-%s-%s.%s" % (file_id, itag, extension)
        full_name = os.path.join(datadir, full_name)
        if os.path.exists(full_name):
            continue
        chunk.sort()
        buffer = b""
        for start, end, data in chunk:
            buffer += data
        with open(full_name, "wb") as f:
            f.write(buffer)


def get_cached_data(request, datadir=_DEFAULT_DATA_DIR):
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
    fn = os.path.join(datadir, fn)
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
    from mitmproxy import http
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


if __name__ == "__main__":
    from mitmproxy.tools.main import mitmdump

    script = _HERE + "/playback.py"
    sys.argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sys.argv[0])
    sys.argv[1:] = [
        "-S",
        "data/%s.playback" % sys.argv[1],
        "-s",
        script,
        "-k",
        "--server-replay-nopop",
    ]
    sys.exit(mitmdump())
