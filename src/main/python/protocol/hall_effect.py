# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes.keycodes import Keycode, RESET_KEYCODE
from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET, CMD_VIAL_HALL_EFFECT_SET, CMD_VIAL_HALL_EFFECT_RESET
from unlocker import Unlocker


class ProtocolHallEffect(BaseProtocol):

    def reload_hall_effect(self):
        data = self.usb_send(
            self.dev,
            struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET),
            retries=20
        )
        if data[0] == 0:
            self.key_settings = struct.unpack("<BBHH", data[1:1 + struct.calcsize("<BBHH")])
        else:
            self.key_settings = -1

    def hall_effect_get(self):
        return self.key_settings

    def hall_effect_set(self, settings):
        if self.key_settings == settings:
            return
        
        self.key_settings = settings
        
        serialized = struct.pack("<BBHH", *settings)
        self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_SET) + serialized, retries=20)

    # def hall_effect_reset(self):
    #     self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_RESET))

    def save_hall_effect(self):
        return self.key_settings

    def restore_hall_effect(self, data):
        self.hall_effect_set(data)
