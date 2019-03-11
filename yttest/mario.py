"""
Drives the browser during the playback test.
"""
from marionette_harness import Marionette
from marionette_driver.by import By


def execute_script(script, context="chrome"):
    client = Marionette(host='localhost', port=2828)
    client.start_session()

    with client.using_context(context):
        res = client.execute_script(script)

    client.close()
    return res
