#!/usr/bin/env python3.4
#
# Copyright 2017 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import unittest

from mobly.controllers.android_device_lib import callback_handler
from mobly.controllers.android_device_lib import jsonrpc_client_base

MOCK_CALLBACK_ID = "1-0"
MOCK_RAW_EVENT = {
    'callbackId': '2-1',
    'name': 'AsyncTaskResult',
    'time': 20460228696,
    'data': {
        'exampleData': "Here's a simple event.",
        'successful': True,
        'secretNumber': 12
    }
}


class CallbackHandlerTest(unittest.TestCase):
    """Unit tests for mobly.controllers.android_device_lib.callback_handler.
    """

    def test_timeout_value(self):
        self.assertGreaterEqual(jsonrpc_client_base._SOCKET_READ_TIMEOUT,
                                callback_handler.MAX_TIMEOUT)

    def test_event_dict_to_snippet_event(self):
        mock_event_client = mock.Mock()
        mock_event_client.eventWaitAndGet = mock.Mock(
            return_value=MOCK_RAW_EVENT)
        handler = callback_handler.CallbackHandler(
            callback_id=MOCK_CALLBACK_ID,
            event_client=mock_event_client,
            ret_value=None,
            method_name=None)
        event = handler.waitAndGet('ha')
        self.assertEqual(event.name, MOCK_RAW_EVENT['name'])
        self.assertEqual(event.creation_time, MOCK_RAW_EVENT['time'])
        self.assertEqual(event.data, MOCK_RAW_EVENT['data'])
        self.assertEqual(event.callback_id, MOCK_RAW_EVENT['callbackId'])

    def test_wait_and_get_timeout(self):
        mock_event_client = mock.Mock()
        java_timeout_msg = 'com.google.android.mobly.snippet.event.EventSnippet$EventSnippetException: timeout.'
        mock_event_client.eventWaitAndGet = mock.Mock(
            side_effect=jsonrpc_client_base.ApiError(java_timeout_msg))
        handler = callback_handler.CallbackHandler(
            callback_id=MOCK_CALLBACK_ID,
            event_client=mock_event_client,
            ret_value=None,
            method_name=None)
        expected_msg = 'Timeout waiting for event "ha" .*'
        with self.assertRaisesRegexp(callback_handler.TimeoutError,
                                     expected_msg):
            handler.waitAndGet('ha')


if __name__ == "__main__":
    unittest.main()