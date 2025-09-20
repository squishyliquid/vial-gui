# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QSlider, \
   QComboBox, QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from editor.basic_editor import BasicEditor
from widgets.keyboard_widget import KeyboardWidget
from util import tr
from vial_device import VialKeyboard

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
        empty_space_widget.clicked.connect(self.on_empty_space_clicked)
        self.addWidget(empty_space_widget)

        settings_widget = QWidget()
        settings_layout = QHBoxLayout()
        # settings_layout.setContentsMargins(52, 0, 0, 0)
        settings_widget.setLayout(settings_layout)

        #
        # --- Group 1: Global ---
        #
        group_global = QGroupBox("")
        group_global_layout = QGridLayout()
        group_global.setMinimumWidth(215)
        group_global.setLayout(group_global_layout)

        # Travel distance
        self.lbl_travel_dist = QLabel(tr("HallEffect", "Travel distance"))
        group_global_layout.addWidget(self.lbl_travel_dist, 0, 0)
        self.travel_dist = QComboBox()
        self.travel_dist.addItems(["3.2 mm", "3.4 mm", "3.5 mm", "3.8 mm", "3.9 mm"])
        self.travel_dist.currentTextChanged.connect(self.on_travel_dist_changed)
        group_global_layout.addWidget(self.travel_dist, 1, 0, 1, 4)

        blank_label = QLabel("")   # empty string
        group_global_layout.addWidget(blank_label, 2, 0, 1, 3)

        # Sensitivity
        self.lbl_sensitivity = QLabel(tr("HallEffect", "Sensitivity"))
        self.lbl_high_sensitivity = QLabel(tr("HallEffect", "High"))
        self.lbl_low_sensitivity = QLabel(tr("HallEffect", "Low"))
        group_global_layout.addWidget(self.lbl_sensitivity, 3, 0)
        self.sensitivity = QSlider(QtCore.Qt.Horizontal)
        self.sensitivity.setRange(2, 20)
        self.sensitivity.valueChanged.connect(self.on_sensitivity_changed)
        group_global_layout.addWidget(self.sensitivity, 4, 0, 1, 3)
        self.txt_sensitivity = QLabel()
        # self.txt_sensitivity.setStyleSheet("""
        #     background-color: #353535;
        #     border-radius: 4px;
        #     padding: 4px;
        # """)
        group_global_layout.addWidget(self.txt_sensitivity, 4, 3, alignment=Qt.AlignTop)
        group_global_layout.addWidget(self.lbl_high_sensitivity, 5, 0, alignment=Qt.AlignTop)
        group_global_layout.addWidget(self.lbl_low_sensitivity, 5, 2, alignment=Qt.AlignTop | Qt.AlignRight)

        settings_layout.addWidget(group_global)
        
        #
        # --- Group 2: Per key ---
        #
        group_per_key = QGroupBox("")
        group_per_key_layout = QGridLayout()
        group_per_key.setMinimumWidth(215)
        group_per_key.setLayout(group_per_key_layout)

        # Actuation point
        self.lbl_actuation = QLabel(tr("HallEffect", "Actuation point"))
        group_per_key_layout.addWidget(self.lbl_actuation, 0, 0)
        self.actuation = QSlider(QtCore.Qt.Horizontal)
        # self.actuation = QSlider(QtCore.Qt.Vertical)
        # self.actuation.setInvertedAppearance(1)
        self.actuation.setMinimum(1)
        self.actuation.valueChanged.connect(self.on_actuation_changed)
        group_per_key_layout.addWidget(self.actuation, 1, 0, 1, 3)
        self.txt_actuation = QLabel()
        # self.txt_actuation.setStyleSheet("""
        #     background-color: #353535;
        #     border-radius: 4px;
        #     padding: 4px;
        # """)
        group_per_key_layout.addWidget(self.txt_actuation, 1, 3, alignment=Qt.AlignTop)

        blank_label = QLabel("")   # empty string
        group_per_key_layout.addWidget(blank_label, 2, 0, 2, 2)

        # Rapid Trigger
        self.mode = QCheckBox("Rapid Trigger")
        self.mode.stateChanged.connect(self.on_rt_changed)
        group_per_key_layout.addWidget(self.mode, 4, 0, 1, 2)

        # Continuous Rapid Trigger
        self.mode_crt = QCheckBox("Continuous Rapid Trigger")
        self.mode_crt.stateChanged.connect(self.on_crt_changed)
        group_per_key_layout.addWidget(self.mode_crt, 5, 0, 1, 3)

        settings_layout.addWidget(group_per_key)

        #
        # --- Replug warning below groups ---
        #
        self.replug_label = QLabel("⚠️ Unplug and replug keyboard to apply changes")
        self.replug_label.setStyleSheet("font-size: 12px; color: red; font-weight: bold;")
        self.replug_label.setAlignment(Qt.AlignCenter)
        # self.replug_label.setWordWrap(True)
        self.replug_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.replug_label.setVisible(False)

        # Base container for groups + replug label
        empty_space = ClickableWidget()
        # empty_space.clicked.connect(self.on_empty_space_clicked)
        empty_space_layout = QVBoxLayout()
        empty_space.setLayout(empty_space_layout)

        empty_space_layout.addWidget(settings_widget, alignment=Qt.AlignHCenter | Qt.AlignTop)
        empty_space_layout.addWidget(self.replug_label, alignment=Qt.AlignHCenter)
        empty_space_layout.addStretch()

        self.addWidget(empty_space)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

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

            if self.keyboard.hall_effect_get_key_config()[row][col] != (self.val_actuation, self.val_mode):
                changed = True
        else:
            if self.keyboard.hall_effect_get_user_config() != [self.val_travel_dist, self.val_sensitivity]:
                changed = True

        self.btn_apply.setEnabled(changed)
        # self.refresh_layer_display()

    def on_travel_dist_changed(self, dist):
        try:
            travel_dist = int(float(dist.replace(" mm", "")) * 100)
        except ValueError:
            travel_dist = 0
        # print(travel_dist)
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

    def replug_required(self, prev, curr):
        travel_distance_groups = [
            {320},
            {340, 350},
            {380},
            {390}
        ]
        prev_group = next((i for i, g in enumerate(travel_distance_groups) if prev in g), None)
        curr_group = next((i for i, g in enumerate(travel_distance_groups) if curr in g), None)

        # Replug required if both are valid and they belong to different groups
        return prev_group is not None and curr_group is not None and prev_group != curr_group

    def set_replug_required(self, required: bool):
        self.replug_label.setVisible(required)

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
                    actuation = self.keyboard.hall_effect_get_key_config()[row][col][0]
                    mode = self.keyboard.hall_effect_get_key_config()[row][col][1]
                    if actuation >= self.val_travel_dist:
                        self.keyboard.hall_effect_set_key_config(row, col, (self.val_travel_dist - 10, mode))
                        changed = True
                if changed:
                    self.refresh_layer_display()

            prev = self.replug_value_check
            curr = self.val_travel_dist
            self.set_replug_required(self.replug_required(prev, curr))

            self.keyboard.hall_effect_set_user_config(0, self.val_travel_dist)
            self.keyboard.hall_effect_set_user_config(1, self.val_sensitivity)

            self.on_change()

    def apply_all(self):
        self.prev_key = None
        config = (self.val_actuation, self.val_mode)

        for widget in self.container.widgets:
            row = widget.desc.row
            col = widget.desc.col

            if (self.keyboard.hall_effect_get_key_config()[row][col] != (self.val_actuation, self.val_mode)):
                self.keyboard.hall_effect_set_key_config(row, col, config)

        self.on_change()
        self.container.deselect()
        self.refresh_layer_display()

    def reload_settings(self):
        self.prev_key = None

        row = self.container.widgets[0].desc.row
        col = self.container.widgets[0].desc.col

        self.val_actuation = self.keyboard.hall_effect_get_key_config()[row][col][0]
        self.val_mode = self.keyboard.hall_effect_get_key_config()[row][col][1]
        self.val_travel_dist = self.keyboard.hall_effect_get_user_config()[0]
        self.val_sensitivity = self.keyboard.hall_effect_get_user_config()[1]
        
        self.update_mode(self.val_mode)
        self.update_sensitivity(self.val_sensitivity / 5)
        self.update_actuation(self.val_actuation / 10)
        self.update_travel_dist(self.val_travel_dist / 100)

        self.replug_value_check = self.keyboard.hall_effect_get_user_config()[0]
        self.set_replug_required(False)

        self.btn_apply_all.setEnabled(False)

        # Enable widgets
        enable_widgets = [self.lbl_travel_dist, self.travel_dist, self.sensitivity, 
                        self.txt_sensitivity, self.lbl_sensitivity, self.lbl_high_sensitivity, self.lbl_low_sensitivity]
        for widget in enable_widgets:
            widget.setEnabled(True)

        # Disable widgets
        disable_widgets = [self.lbl_actuation, self.txt_actuation, self.actuation, self.mode, self.mode_crt]
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

    def on_empty_space_clicked(self):
        self.container.deselect()
        # self.container.update()
        # self.refresh_layer_display()
        
    def on_key_clicked(self):
        self.val_travel_dist = self.keyboard.hall_effect_get_user_config()[0]
        self.val_sensitivity = self.keyboard.hall_effect_get_user_config()[1]
        
        self.update_sensitivity(self.val_sensitivity / 5)
        self.update_travel_dist(self.val_travel_dist / 100)

        row, col = self.container.active_key.desc.row, self.container.active_key.desc.col

        # print(self.container.active_key)

        if self.prev_key == self.container.active_key:
            self.container.deselect()
            self.prev_key = None
            return

        self.prev_key = self.container.active_key
        self.btn_apply_all.setEnabled(True)

        # Disable elements
        for widget in [self.lbl_travel_dist, self.travel_dist, self.sensitivity, 
                    self.txt_sensitivity, self.lbl_sensitivity, self.lbl_high_sensitivity, self.lbl_low_sensitivity]:
            widget.setEnabled(False)

        # Enable elements
        for widget in [self.lbl_actuation, self.txt_actuation, self.actuation, self.mode, self.mode_crt]:
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
                        self.txt_sensitivity, self.lbl_sensitivity, self.lbl_high_sensitivity, self.lbl_low_sensitivity]
        for widget in enable_widgets:
            widget.setEnabled(True)

        # Disable widgets
        disable_widgets = [self.lbl_actuation, self.txt_actuation, self.actuation, self.mode, self.mode_crt]
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