# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QSlider, \
   QComboBox, QCheckBox

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal

from editor.basic_editor import BasicEditor
from widgets.keyboard_widget import KeyboardWidget
from util import tr
from vial_device import VialKeyboard

from PyQt5.QtGui import QColor

import json
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class ClickableWidget(QWidget):

    clicked = pyqtSignal()

    def mousePressEvent(self, evt):
        super().mousePressEvent(evt)
        self.clicked.emit()

class HallEffect(BasicEditor):
    def __init__(self, layout_editor):
        super().__init__()
        self.layout_editor = layout_editor

        # Initialize keyboard container
        self.container = KeyboardWidget(layout_editor)
        self.container.clicked.connect(self.on_key_clicked)
        self.container.deselected.connect(self.on_key_deselected)

        # Main layout setup
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(self.container)
        main_layout.addStretch()
        main_layout.setAlignment(self.container, Qt.AlignHCenter)

        # Clickable widget for empty space
        empty_space_widget = ClickableWidget()
        empty_space_widget.setLayout(main_layout)
        # empty_space_widget.clicked.connect(self.on_empty_space_clicked)
        self.addWidget(empty_space_widget)

        settings_widget = QWidget()
        #settings_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        settings_layout = QGridLayout()
        settings_widget.setLayout(settings_layout)

        # Travel distance
        self.lbl_travel_dist = QLabel(tr("HallEffect", "Travel distance"))
        settings_layout.addWidget(self.lbl_travel_dist, 0, 0)
        self.travel_dist = QComboBox()
        self.travel_dist.addItems(["3.4 mm", "3.5 mm"])
        self.travel_dist.currentTextChanged.connect(self.on_travel_dist_changed)
        settings_layout.addWidget(self.travel_dist, 0, 1)

        # Actuation point
        self.lbl_actuation = QLabel(tr("HallEffect", "Actuation point"))
        settings_layout.addWidget(self.lbl_actuation, 1, 0)
        self.actuation = QSlider(QtCore.Qt.Horizontal)
        self.actuation.setMinimum(1)
        self.actuation.valueChanged.connect(self.on_actuation_changed)
        settings_layout.addWidget(self.actuation, 1, 1)
        self.txt_actuation = QLabel()
        settings_layout.addWidget(self.txt_actuation, 1, 2)

        # Rapid Trigger
        self.mode = QCheckBox("Rapid Trigger")
        self.mode.stateChanged.connect(self.on_rt_changed)
        settings_layout.addWidget(self.mode, 2, 0)

        # Sensitivity
        self.lbl_sensitivity = QLabel(tr("HallEffect", "Sensitivity"))
        settings_layout.addWidget(self.lbl_sensitivity, 3, 0)
        self.sensitivity = QSlider(QtCore.Qt.Horizontal)
        self.sensitivity.setRange(2, 20)
        self.sensitivity.valueChanged.connect(self.on_sensitivity_changed)
        settings_layout.addWidget(self.sensitivity, 3, 1)
        self.txt_sensitivity = QLabel()
        settings_layout.addWidget(self.txt_sensitivity, 3, 2)

        # # Continuous Rapid Trigger
        self.mode_crt = QCheckBox("Continuous RT")
        self.mode_crt.stateChanged.connect(self.on_crt_changed)
        settings_layout.addWidget(self.mode_crt, 4, 0)

        # Create the ClickableWidget as the base container
        empty_space = ClickableWidget()
        # empty_space.clicked.connect(self.on_empty_space_clicked)

        # Create a layout for the ClickableWidget
        empty_space_layout = QVBoxLayout()
        empty_space.setLayout(empty_space_layout)

        # Add stretch above and below the settings_widget for centering
        #empty_space_layout.addStretch()
        empty_space_layout.addWidget(settings_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
        empty_space_layout.addStretch()

        self.addWidget(empty_space)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Add stretch to the left of the buttons

        self.btn_apply = QPushButton(tr("HallEffect", "Apply"))
        self.btn_apply.clicked.connect(self.apply)
        button_layout.addWidget(self.btn_apply)

        self.btn_apply_all = QPushButton(tr("HallEffect", "Apply to all"))
        self.btn_apply_all.clicked.connect(self.apply_all)
        button_layout.addWidget(self.btn_apply_all)

        self.addLayout(button_layout)

    def on_change(self):
        changed = False
        if self.container.active_key != None:
            row = self.container.active_key.desc.row
            col = self.container.active_key.desc.col
            if row in self.keyboard.active_rows:
                if self.keyboard.hall_effect_get_key_config()[row][col] != (self.val_actuation, self.val_mode):
                    changed = True
        else:
            if self.keyboard.hall_effect_get_user_config() != [self.val_travel_dist, self.val_sensitivity]:
                changed = True

        self.btn_apply.setEnabled(changed)
        # self.refresh_layer_display()

    def on_travel_dist_changed(self, dist):
        travel_dist = 0
        if dist == "3.4 mm":
            travel_dist = 340
        elif dist == "3.5 mm":
            travel_dist = 350
        
        self.actuation.setMaximum(int(travel_dist / 10 - 1))
        self.val_travel_dist = travel_dist
        self.on_change()

    def on_actuation_changed(self, actuation):
        self.val_actuation = actuation * 10
        self.txt_actuation.setText(f'{actuation / 10:.1f} mm')
        self.on_change()

    def on_rt_changed(self, mode):
        if mode == 2:
            mode = 1
        self.val_mode = mode
        self.mode_crt.setEnabled(mode)
        if mode == 0:
            self.mode_crt.setChecked(mode)        
        self.on_change()

    def on_crt_changed(self, mode):
        if mode == 0:
            mode = 1
        if self.val_mode != 0:
            self.val_mode = mode
            self.on_change()

    def on_sensitivity_changed(self, sensitivity):
        self.val_sensitivity = sensitivity * 5
        self.txt_sensitivity.setText(f'{sensitivity * 0.05:.2f} mm')
        self.on_change()

    def apply(self):
        if self.container.active_key != None:
            self.prev_key = None
            row = self.container.active_key.desc.row
            col = self.container.active_key.desc.col
            config = (self.val_actuation, self.val_mode)
            self.keyboard.hall_effect_set_key_config(row, col, config)

            self.on_change()
            self.container.deselect()
            self.refresh_layer_display()
        else:
            if self.keyboard.hall_effect_get_user_config()[0] > self.val_travel_dist:
                changed = False
                for widget in self.container.widgets:
                    row = widget.desc.row
                    col = widget.desc.col
                    if row in self.keyboard.active_rows:
                        actuation = self.keyboard.hall_effect_get_key_config()[row][col][0]
                        mode = self.keyboard.hall_effect_get_key_config()[row][col][1]
                        if actuation >= self.val_travel_dist:
                            self.keyboard.hall_effect_set_key_config(row, col, (self.val_travel_dist - 10, mode))
                            changed = True
                if changed:
                    self.refresh_layer_display()

            self.keyboard.hall_effect_set_user_config(0, self.val_travel_dist)
            self.keyboard.hall_effect_set_user_config(1, self.val_sensitivity)

            self.on_change()

    def apply_all(self):
        self.prev_key = None
        config = (self.val_actuation, self.val_mode)

        for widget in self.container.widgets:
            row = widget.desc.row
            col = widget.desc.col
            if row in self.keyboard.active_rows:
                if (self.keyboard.hall_effect_get_key_config()[row][col] != (self.val_actuation, self.val_mode)):
                    self.keyboard.hall_effect_set_key_config(row, col, config)

        self.on_change()
        self.container.deselect()
        self.refresh_layer_display()

    def reload_settings(self):
        self.prev_key = None

        row = self.keyboard.active_rows[0]
        col = 0

        for widget in self.container.widgets:
            row = widget.desc.row
            col = widget.desc.col

            if row in self.keyboard.active_rows:
                break

        # print(row, col)

        self.val_actuation = self.keyboard.hall_effect_get_key_config()[row][col][0]
        self.val_mode = self.keyboard.hall_effect_get_key_config()[row][col][1]
        self.val_travel_dist = self.keyboard.hall_effect_get_user_config()[0]
        self.val_sensitivity = self.keyboard.hall_effect_get_user_config()[1]
        
        self.update_mode(self.val_mode)
        self.update_sensitivity(self.val_sensitivity / 5)
        self.update_actuation(self.val_actuation / 10)
        self.update_travel_dist(self.val_travel_dist / 100)

        self.btn_apply_all.setEnabled(False)

        # Enable widgets
        enable_widgets = [self.lbl_travel_dist, self.travel_dist, self.sensitivity, 
                        self.txt_sensitivity, self.lbl_sensitivity]
        for widget in enable_widgets:
            widget.setEnabled(True)

        # Disable widgets
        disable_widgets = [self.lbl_actuation, self.actuation, self.mode, self.mode_crt]
        for widget in disable_widgets:
            widget.setEnabled(False)

        self.on_change()

    def update_mode(self, mode):
        self.mode.setChecked(mode)
        if mode == 2:
            self.mode_crt.setChecked(1)
        else:
            self.mode_crt.setChecked(0)
        self.mode_crt.setEnabled(mode)

    def update_sensitivity(self, sensitivity):
        self.sensitivity.setSliderPosition(int(sensitivity))
        self.txt_sensitivity.setText(f'{sensitivity * 0.05:.2f} mm')

    def update_travel_dist(self, dist):
        self.travel_dist.setCurrentText(f'{dist:.1f} mm')
        self.actuation.setMaximum(int(dist * 10 - 1))

    def update_actuation(self, actuation):
        self.actuation.setSliderPosition(int(actuation))
        self.txt_actuation.setText(f'{actuation / 10:.1f} mm')

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """
        for widget in self.container.widgets:
            row = widget.desc.row
            col = widget.desc.col

            if row in self.keyboard.active_rows:
                actuation = self.keyboard.hall_effect_get_key_config()[row][col][0]
                mode = self.keyboard.hall_effect_get_key_config()[row][col][1]
                widget.setText(f"{actuation/100:.1f}")
                
                if mode == 0:
                    widget.setColor(QColor(0, 0, 0))
                elif mode == 1:
                    widget.setColor(QColor(255, 255, 255))
                elif mode == 2:
                    widget.setColor(QColor(135, 206, 250))
        self.container.update()

    # def on_empty_space_clicked(self):
    #     self.container.deselect()
    #     self.container.update()
        
    def on_key_clicked(self):
        self.val_travel_dist = self.keyboard.hall_effect_get_user_config()[0]
        self.val_sensitivity = self.keyboard.hall_effect_get_user_config()[1]
        
        self.update_sensitivity(self.val_sensitivity / 5)
        self.update_travel_dist(self.val_travel_dist / 100)

        row, col = self.container.active_key.desc.row, self.container.active_key.desc.col

        # print(self.container.active_key)

        if row not in self.keyboard.active_rows:
            self.container.deselect()
            self.prev_key = None
            return

        if self.prev_key == self.container.active_key:
            self.container.deselect()
            self.prev_key = None
            return

        self.prev_key = self.container.active_key
        self.btn_apply_all.setEnabled(True)

        # Disable elements
        for widget in [self.lbl_travel_dist, self.travel_dist, self.sensitivity, 
                    self.txt_sensitivity, self.lbl_sensitivity]:
            widget.setEnabled(False)

        # Enable elements
        for widget in [self.lbl_actuation, self.actuation, self.mode, self.mode_crt]:
            widget.setEnabled(True)

        key_config = self.keyboard.hall_effect_get_key_config()[row][col]
        self.update_actuation(key_config[0] / 10)
        self.update_mode(key_config[1])

    def on_key_deselected(self):
        if self.prev_key != None:
            row, col = self.prev_key.desc.row, self.prev_key.desc.col
            key_config = self.keyboard.hall_effect_get_key_config()[row][col]
            self.update_actuation(key_config[0] / 10)
            self.update_mode(key_config[1])
            self.prev_key = None

        self.val_travel_dist = self.keyboard.hall_effect_get_user_config()[0]
        self.val_sensitivity = self.keyboard.hall_effect_get_user_config()[1]
        
        self.update_sensitivity(self.val_sensitivity / 5)
        self.update_travel_dist(self.val_travel_dist / 100)

        self.btn_apply_all.setEnabled(False)

        # Enable widgets
        enable_widgets = [self.lbl_travel_dist, self.travel_dist, self.sensitivity, 
                        self.txt_sensitivity, self.lbl_sensitivity]
        for widget in enable_widgets:
            widget.setEnabled(True)

        # Disable widgets
        disable_widgets = [self.lbl_actuation, self.actuation, self.mode, self.mode_crt]
        for widget in disable_widgets:
            widget.setEnabled(False)
        
        self.on_change()

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.container.set_keys(self.keyboard.keys, self.keyboard.encoders)
            self.refresh_layer_display()
            self.reload_settings()

        self.container.setEnabled(self.valid())

    def valid(self):
        return isinstance(self.device, VialKeyboard) # and \
            #    (self.device.keyboard and self.device.keyboard.key_config != -1 and self.device.keyboard.user_config != -1)