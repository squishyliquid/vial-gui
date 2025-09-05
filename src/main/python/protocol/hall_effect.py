# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes.keycodes import Keycode, RESET_KEYCODE
from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET_KEY_CONFIG, CMD_VIAL_HALL_EFFECT_SET_KEY_CONFIG, CMD_VIAL_HALL_EFFECT_GET_USER_CONFIG, CMD_VIAL_HALL_EFFECT_SET_USER_CONFIG, CMD_VIAL_HALL_EFFECT_GET_HANDEDNESS
from unlocker import Unlocker


class ProtocolHallEffect(BaseProtocol):

    def reload_hall_effect(self):
        # data = self.usb_send(
        #     self.dev,
        #     struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET_HANDEDNESS),
        #     retries=20
        # )
        
        self.key_config = []
        for row in range(self.rows):
            r = []
            for col in range(self.cols):
                data = self.usb_send(
                    self.dev,
                    struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET_KEY_CONFIG, row, col),
                    retries=20
                )
                if data[0] == 0:
                    # self.key_settings = struct.unpack("<BBHH", data[1:1 + struct.calcsize("<BBHH")])
                    r.append(struct.unpack("<HB", data[1:1 + struct.calcsize("<HB")]))
                else:
                    self.key_config = -1
                    break
            self.key_config.append(r)
        
        self.user_config = []
        for i in range(2):
            data = self.usb_send(
                self.dev,
                struct.pack("BBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_GET_USER_CONFIG, i),
                retries=20
            )
            if data[0] == 0:
                self.user_config.append(struct.unpack("<H", data[1:1 + struct.calcsize("<H")])[0])
            else:
                self.user_config = -1
                break

    def hall_effect_get_key_config(self):
        return self.key_config
    
    def hall_effect_get_user_config(self):
        return self.user_config

    def hall_effect_set_key_config(self, row, col, config):
        if self.key_config[row][col] == config:
            return
        
        self.key_config[row][col] = config
        serialized = struct.pack("<HB", *config)
        self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_SET_KEY_CONFIG, row, col) + serialized, retries=20)

    def hall_effect_set_user_config(self, idx, config):
        if self.user_config[idx] == config:
            return
        
        self.user_config[idx] = config
        serialized = struct.pack("<H", *(config,))
        self.usb_send(self.dev, struct.pack("BBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_SET_USER_CONFIG, idx) + serialized, retries=20)

    # def hall_effect_reset(self):
    #     self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_HALL_EFFECT_RESET))

    def save_hall_effect(self):
        return [self.key_config, self.user_config]

    def restore_hall_effect(self, data):
        key_cfg = data[0]
        # print(data[0])
        user_cfg = data[1]
        # print(data[1])

        for row in range(self.rows):
            for col in range(self.cols):
                self.hall_effect_set_key_config(row, col, key_cfg[row][col])

        self.hall_effect_set_user_config(0, user_cfg[0])
        self.hall_effect_set_user_config(1, user_cfg[1])