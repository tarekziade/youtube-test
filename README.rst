=============
Youtube proxy
=============

This project allows you to record and playback youtube videos for testing.

How things work
---------------

When the Youtube client loads, it calls the server to get chunks of
audio and video data with a request on::

  https://someserver.googlevideo.com/videoplayback?itag=XXX&range=A:B

Where **itag** is the quality of the video, defined by an integer
see the full list at https://github.com/tarekziade/youtube-test/blob/master/yttest/util.py#L9
and **range** is the bytes requested for the video.

The Youtube client can change the quality on the fly during playback,
and request arbitrary chunks, so a regular proxy will record one single
combination of playback for the video. The sequence of chunks asked from the
server may vary depending on the network and user activity, and a recorded
playback may fail on a following run.

In order to provide a reliable proxy for reproducible local playbacks, and
treat the YT client as a black box, the audio and video files are rebuilt
locally so any chunk can be returned when requested. For a given YT video, if
the video is fully played on all qualities, the proxy will have all the chunks.

It's required to update the recorded chunks on a regular basis to avoid
a regression in case the youtube client or server change.


Installation
------------

::

 $ virtualenv .
 $ bin/pip install -r requirements.txt
 $ bin/python setup.py develop

Add a .mitmproxy/config.yaml file in your home dir::

  upstream_cert: False
  ssl_insecure: True
  anticache: True
  keepserving: True
  stream_large_bodies: 5m
  server_replay_nopop: True

Install the mitm certificate by visiting mitm.it

Record
------

Go to youtube and select a short video, for example: https://www.youtube.com/watch?v=wvpZZqmnNhg

To start the proxy in record mode, run ::

   $ bin/python yttest/record.py wvpZZqmnNhg

Where wvpZZqmnNhg is the id of the video.

Set firefox to use 127.0.0.1:8080 as a proxy server.
Play the video in all quality to fill the proxy cache.

Stop the proxy. The data/ directory will contain all audio and video files.

Playback
--------


To start the proxy in playback mode, run ::

   $ bin/python yttest/playback.py wvpZZqmnNhg

Then visit the browser at https://www.youtube.com/watch?v=wvpZZqmnNhg



