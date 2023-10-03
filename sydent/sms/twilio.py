# Copyright 2016 OpenMarket Ltd
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

import logging
from random import choice
from typing import TYPE_CHECKING, Dict, Optional, cast

from twilio.rest import Client
from twisted.web.http_headers import Headers

from sydent import config
from sydent.http.httpclient import SimpleHttpClient
from sydent.types import JsonDict

if TYPE_CHECKING:
    from sydent.sydent import Sydent

logger = logging.getLogger(__name__)
from_ = config.sms.twilio_num
is_random = config.sms.twilio_random


class TwilioSMS:
    def __init__(self, sydent: "Sydent") -> None:
        self.sydent = sydent
        self.http_cli = SimpleHttpClient(sydent)
        account_sid = self.sydent.config.sms.api_username
        auth_token = self.sydent.config.sms.api_password
        self.client = Client(account_sid, auth_token)

    async def sendTextSMS(self, body: str, dest: str, **kwargs) -> None:

        """
        Sends a text message with the given body to the given MSISDN.

        :param body: The message to send.
        :param dest: The destination MSISDN to send the text message to.
        """
        send_body = {
            "body": body,
            "dest": dest
            },
        
        if is_random:
            send_body["from_"] = choice(from_)
        else:
            send_body["from_"] = from_[0]

        message = self.client.messages.create(
            from_ = send_body["from_"],
            body = send_body["body"],
            to = send_body["dest"],
        )

        response_sid = message.sid
        response_status = message.status
        response_error_code = message.error_code
        response_error_message = message.error_message

        warnlist = [
    13000, 82001, 13612, 81002, 21227, 13241, 80911, 21222, 21229, 52052,
    32702, 13234, 32303, 32301, 94403, 21302, 13616, 13618, 13310, 13328,
    13332, 13335, 40001, 32701, 13330, 45376, 16102, 16101, 23004, 80403,
    45308, 32019, 32102, 21263, 23002, 23005, 80607, 53616, 13230, 13222,
    32112, 13617, 45711, 53620, 45362, 13805, 53621, 80606, 13331, 13252,
    80904, 40005, 13212, 13611, 32021, 32101, 32009, 80614, 80602, 53661,
    60723, 32503, 80903, 13329, 60719, 45719, 13233, 13333, 45307, 60721,
    13313, 14101, 32007, 13510, 60727, 13614, 21226, 31953, 80206, 60709,
    32014, 80906, 13226, 52172, 32006, 13615, 13326, 53632, 21711, 63046,
    13610, 81025, 45206, 13220, 80105, 60325, 13910, 80407, 31930, 13246,
    32103, 81005, 32603, 14111, 45208, 80303, 80905, 61004, 52304, 13217,
    80503, 60702, 13242, 13245, 30105, 32008, 20104, 21710, 53622, 32711,
    13312, 13521, 16113, 13221, 32215, 60714, 80624, 13251, 13430, 52305,
    45302, 30125, 53662, 45375, 82004, 80604, 32113, 22222, 80304, 52401,
    60707, 60333, 80605, 13112, 94100, 13327, 53605, 14106, 13248, 13244,
    30131, 52072, 13223, 52307, 14108, 32304, 80406, 13218, 30104, 80901,
    48001, 80307, 14105, 80409, 21224, 13810, 53625, 32015, 53614, 32212,
    52174, 13322, 13254, 53611, 81018, 13210, 60710, 13511, 32105, 22221,
    32111, 30026, 14241, 30039, 13321, 32100, 13253, 80201, 13520, 45402,
    32401, 53613, 60722, 45353, 80910, 32110, 45305, 50610, 21262, 53607,
    32002, 40153, 13237, 31950, 80405, 13250, 13314, 80909, 80610, 32012,
    52301, 13211, 32114, 32710, 32011, 13410, 53623, 80202, 13232, 21708,
    13619, 53660, 60725, 31951, 13213, 80701, 32703, 13249, 13215, 52303,
    456001, 32214, 456002, 45401, 21225, 94101, 13235, 13236, 53631, 14109,
    81001, 13513, 31931, 21223, 45303, 15003, 60708, 80205, 81000, 21228,
    80908, 13219, 80601, 14207, 13710, 23001, 14104, 80402, 21221, 20001,
    13512, 60409, 13613, 52147, 61006, 13620, 80609, 23003, 53610, 45368,
    13256, 13214, 80408, 13243, 53604, 13320, 13334, 80102, 32502, 13255,
    45715, 14102, 53612, 45306, 13699, 12200, 23006, 80907, 52173, 63037,
    60726, 60724, 14110, 81020, 80104, 53624, 53121, 32302, 53606, 14103,
    13311, 30018, 53615, 13216, 30025, 80401, 45204
    ]
        warnlist_set = set(warnlist)

        if response_error_code >= 400 and response_error_code not in warnlist_set:
            raise Exception(
                "Twilio API responded with status %d (request ID: %s) - %s"
                % (
                    response_error_code,
                    response_sid,
                    response_error_message
                ),
            )

        sid = response_sid

        logger.info(
            "Successfully sent SMS (SID: %s, Status %s)",
            sid,
            response_status,
        )
