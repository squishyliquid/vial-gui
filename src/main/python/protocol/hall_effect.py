# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes.keycodes import Keycode, RESET_KEYCODE
from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_HE_ACTUATION_CONFIG, CMD_VIAL_SET_HE_ACTUATION_CONFIG, \
                                CMD_VIAL_GET_HE_INPUT_PRIORITY_PAIR, CMD_VIAL_SET_HE_INPUT_PRIORITY_PAIR, \
                                CMD_VIAL_GET_HE_SWITCH, CMD_VIAL_SET_HE_SWITCH, CMD_VIAL_HE_RESET, CMD_VIAL_GET_HE_SPECIAL_LAYER, CMD_VIAL_SET_HE_SPECIAL_LAYER
from unlocker import Unlocker

class ActuationConfig:
    
    def __init__(self, actuation_point=0, rt_mode=0, rt_press=0, rt_release=0):
        self.actuation_point = actuation_point
        self.rt_mode = rt_mode
        self.rt_press = rt_press
        self.rt_release = rt_release

    def to_tuple(self):
        return (self.actuation_point, self.rt_mode, self.rt_press, self.rt_release)
    
    def to_dict(self):
        return {
            "actuation_point": self.actuation_point,
            "rt_mode": self.rt_mode,
            "rt_press": self.rt_press,
            "rt_release": self.rt_release
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            actuation_point=data["actuation_point"],
            rt_mode=data["rt_mode"],
            rt_press=data["rt_press"],
            rt_release=data["rt_release"]
        )

class ProtocolHallEffect(BaseProtocol):

    def reload_hall_effect(self):
        self.actuation_matrix = []
        error_occurred = False
        self.firmware_updated = True

        for profile in range(2):
            profile_data = []
            for row in range(self.rows):

                r = []
                for col in range(self.cols):
                    data = self.usb_send(
                        self.dev,
                        struct.pack("BBBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_HE_ACTUATION_CONFIG, profile, row, col),
                        retries=20
                    )
                    if data and data[0] == 0:
                        actuation_tuple = struct.unpack("<BBBB", data[1:1 + struct.calcsize("<BBBB")])
                        actuation_object = ActuationConfig(*actuation_tuple) 
                        r.append(actuation_object)
                    else:
                        error_occurred = True

                profile_data.append(r)

            self.actuation_matrix.append(profile_data)
        
        self.input_priority_pairs = []
        for index in range(8):
            data = self.usb_send(
                self.dev,
                struct.pack("BBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_HE_INPUT_PRIORITY_PAIR, index),
                retries=20
            )
            if data and data[0] == 0:
                input_priority_tuple = struct.unpack("<BBBBBB", data[1:1 + struct.calcsize("<BBBBBB")])
                if input_priority_tuple[0] != 255:
                    self.input_priority_pairs.append(input_priority_tuple)
                else:
                    break
            else:
                error_occurred = True

        if error_occurred:
            self.actuation_matrix = -1
            self.input_priority_pairs = -1

        self.switch_option = -1

        data = self.usb_send(
            self.dev,
            struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_HE_SWITCH),
            retries=20
        )

        if data and data[0] == 0:
            self.switch_option = struct.unpack("<B", data[1:1 + struct.calcsize("<B")])[0]

        self.special_layer = -1

        data = self.usb_send(
            self.dev,
            struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_HE_SPECIAL_LAYER),
            retries=20
        )

        if data and data[0] == 0:
            self.special_layer = struct.unpack("<B", data[1:1 + struct.calcsize("<B")])[0]

        if any(x == -1 for x in [self.actuation_matrix, self.switch_option, self.special_layer]):
            self.firmware_updated = False

    def set_actuation_config(self, profile, row, col):
        actuation_to_send = self.actuation_matrix[profile][row][col]

        data_tuple = actuation_to_send.to_tuple() 

        serialized = struct.pack("BBBB", *data_tuple)
        command_header = struct.pack("BBBBB", 
                                    CMD_VIA_VIAL_PREFIX, 
                                    CMD_VIAL_SET_HE_ACTUATION_CONFIG, 
                                    profile, 
                                    row, 
                                    col)
        
        data_to_send = command_header + serialized
        self.usb_send(self.dev, data_to_send, retries=20)

    def reset_actuation_profile(self, profile):
        data_tuple = (
            128,
            0,
            0,
            0,
        )
        for row in range(self.rows):
            for col in range(self.cols):
                self.actuation_matrix[profile][row][col] = ActuationConfig(*data_tuple) 

                serialized = struct.pack("BBBB", *data_tuple)
                command_header = struct.pack("BBBBB", 
                                            CMD_VIA_VIAL_PREFIX, 
                                            CMD_VIAL_SET_HE_ACTUATION_CONFIG, 
                                            profile, 
                                            row, 
                                            col)
                
                data_to_send = command_header + serialized
                self.usb_send(self.dev, data_to_send, retries=20)

    def set_input_priority_pair(self, index):
        if index == -1:
            index = len(self.input_priority_pairs) - 1

        data_tuple = self.input_priority_pairs[index]

        serialized = struct.pack("BBBBBB", *data_tuple)
        command_header = struct.pack("BBB", 
                                    CMD_VIA_VIAL_PREFIX, 
                                    CMD_VIAL_SET_HE_INPUT_PRIORITY_PAIR, 
                                    index)
        
        data_to_send = command_header + serialized
        self.usb_send(self.dev, data_to_send, retries=20)

    def set_empty_input_priority_pair(self, index):
        data_tuple = (
            255,
            255,
            255,
            255,
            255,
            255,
        )

        serialized = struct.pack("BBBBBB", *data_tuple)
        command_header = struct.pack("BBB", 
                                    CMD_VIA_VIAL_PREFIX, 
                                    CMD_VIAL_SET_HE_INPUT_PRIORITY_PAIR, 
                                    index)
        
        data_to_send = command_header + serialized
        self.usb_send(self.dev, data_to_send, retries=20)

    def remove_input_priority_pair(self, index_to_remove):
        # if 0 <= index_to_remove < len(self.input_priority_pairs):
        #     self.input_priority_pairs.pop(index_to_remove)
        
        for i in range(index_to_remove, len(self.input_priority_pairs)):
            data_tuple = self.input_priority_pairs[i]

            serialized = struct.pack("BBBBBB", *data_tuple)
            command_header = struct.pack("BBB", 
                                        CMD_VIA_VIAL_PREFIX, 
                                        CMD_VIAL_SET_HE_INPUT_PRIORITY_PAIR, 
                                        i)
            
            data_to_send = command_header + serialized
            self.usb_send(self.dev, data_to_send, retries=20)

        empty_pair = (
            255,
            255,
            255,
            255,
            255,
            255,
        )
        
        for i in range(len(self.input_priority_pairs), 8):
            serialized = struct.pack("BBBBBB", *empty_pair)
            command_header = struct.pack("BBB", 
                                        CMD_VIA_VIAL_PREFIX, 
                                        CMD_VIAL_SET_HE_INPUT_PRIORITY_PAIR, 
                                        i)
            
            data_to_send = command_header + serialized
            self.usb_send(self.dev, data_to_send, retries=20)

    def set_switch_option(self):
        switch_val = self.switch_option

        data_to_send = struct.pack("BBB", 
                                   CMD_VIA_VIAL_PREFIX, 
                                   CMD_VIAL_SET_HE_SWITCH, 
                                   switch_val)
        
        self.usb_send(self.dev, data_to_send, retries=20)

    def set_special_layer(self):
        special_layer_val = self.special_layer
    
        data_to_send = struct.pack("BBB", 
                                   CMD_VIA_VIAL_PREFIX, 
                                   CMD_VIAL_SET_HE_SPECIAL_LAYER, 
                                   special_layer_val)
        
        self.usb_send(self.dev, data_to_send, retries=20)

    def save_hall_effect(self):
        serialized_matrix = []
        
        profiles = len(self.actuation_matrix)
        
        for p in range(profiles):
            profile_list = []
            for r in range(self.rows):
                row_list = []
                for c in range(self.cols):
                    config_obj = self.actuation_matrix[p][r][c]
                    row_list.append(config_obj.to_dict())
                profile_list.append(row_list)
            serialized_matrix.append(profile_list)
        
        he_config = {
            "actuation_matrix": serialized_matrix,
            "input_priority_pairs": self.input_priority_pairs,
            "switch_option": self.switch_option,
            "special_layer": self.special_layer
        }
        
        return he_config
    
    def restore_hall_effect(self, hall_effect_data):
        self.input_priority_pairs = hall_effect_data["input_priority_pairs"]
        self.switch_option = hall_effect_data["switch_option"]
        self.special_layer = hall_effect_data["special_layer"]

        loaded_matrix = hall_effect_data["actuation_matrix"]
        deserialized_matrix = []
        
        for profile_list in loaded_matrix:
            new_profile = []
            for row_list in profile_list:
                new_row = []
                for config_dict in row_list:
                    config_obj = ActuationConfig.from_dict(config_dict)
                    new_row.append(config_obj)
                new_profile.append(new_row)
            deserialized_matrix.append(new_profile)
            
        self.actuation_matrix = deserialized_matrix

        for p in range(2):
            profile_list = []
            for r in range(self.rows):
                row_list = []
                for c in range(self.cols):
                    self.set_actuation_config(p, r, c)

        for i in range(len(self.input_priority_pairs)):
            self.set_input_priority_pair(i)

        for i in range(len(self.input_priority_pairs), 8):
            self.set_empty_input_priority_pair(i)

        self.set_switch_option()
        self.set_special_layer()