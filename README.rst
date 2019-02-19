=============
Youtube proxy
=============

This project allows you to record and playback youtube videos for testing.

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



