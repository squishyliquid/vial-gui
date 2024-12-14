# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QSlider, \
    QComboBox, QCheckBox, QMessageBox

from editor.basic_editor import BasicEditor
from util import tr
from vial_device import VialKeyboard

class HallEffect(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        self.addStretch()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.container = QGridLayout()
        w.setLayout(self.container)
        self.addWidget(w)
        self.setAlignment(w, QtCore.Qt.AlignHCenter)

        lbl_travel_dist = QLabel(tr("HallEffect", "Travel distance"))
        self.container.addWidget(lbl_travel_dist, 0, 0)
        self.travel_dist = QComboBox()
        self.travel_dist.addItem("3.5 mm")
        #self.travel_dist.addItem("4.0 mm")
        self.travel_dist.currentTextChanged.connect(self.on_travel_dist_changed)
        self.container.addWidget(self.travel_dist, 0, 1)
        
        lbl_actuation = QLabel(tr("HallEffect", "Actuation point"))
        self.container.addWidget(lbl_actuation, 1, 0)
        self.actuation = QSlider(QtCore.Qt.Horizontal)
        self.actuation.setMinimum(1)
        self.actuation.valueChanged.connect(self.on_actuation_changed)
        self.container.addWidget(self.actuation, 1, 1)
        self.txt_actuation = QLabel()
        self.container.addWidget(self.txt_actuation, 1, 2)

        self.mode = QCheckBox("Rapid Trigger")
        self.mode.stateChanged.connect(self.on_mode_changed)
        self.container.addWidget(self.mode, 2, 0)

        self.lbl_sensitivity = QLabel(tr("HallEffect", "Sensitivity"))
        self.container.addWidget(self.lbl_sensitivity, 3, 0)
        self.sensitivity = QSlider(QtCore.Qt.Horizontal)
        self.sensitivity.setMinimum(2)
        self.sensitivity.setMaximum(20)
        self.sensitivity.valueChanged.connect(self.on_sensitivity_changed)
        self.container.addWidget(self.sensitivity, 3, 1)
        self.txt_sensitivity = QLabel()
        self.container.addWidget(self.txt_sensitivity, 3, 2)

        self.addStretch()
        buttons = QHBoxLayout()
        buttons.addStretch()
        self.btn_save = QPushButton(tr("HallEffect", "Save"))
        buttons.addWidget(self.btn_save)
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_undo = QPushButton(tr("HallEffect", "Undo"))
        buttons.addWidget(self.btn_undo)
        self.btn_undo.clicked.connect(self.reload_settings)
        # self.btn_reset = QPushButton(tr("HallEffect", "Reset"))
        # buttons.addWidget(self.btn_reset)
        # self.btn_reset.clicked.connect(self.reset_settings)
        self.addLayout(buttons)

    def reload_settings(self):
        self.keyboard.reload_hall_effect()
        settings = self.keyboard.hall_effect_get()
        self.val_mode = settings[0]
        self.val_sensitivity = settings[1]
        self.val_travel_dist = settings[2]
        self.val_actuation = settings[3]
        
        self.update_mode(self.val_mode)
        self.update_sensitivity(self.val_sensitivity/5)
        self.update_actuation(self.val_actuation/10)
        self.update_travel_dist(self.val_travel_dist/100)

        self.on_change()

    def on_change(self):
        changed = False
        
        if self.keyboard.hall_effect_get() != (self.val_mode, self.val_sensitivity, self.val_travel_dist, self.val_actuation):
            changed = True

        self.btn_save.setEnabled(changed)
        self.btn_undo.setEnabled(changed)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.reload_settings()

    def save_settings(self):
        settings = (self.val_mode, self.val_sensitivity, self.val_travel_dist, self.val_actuation)
        self.keyboard.hall_effect_set(settings)
        self.on_change()

    # def reset_settings(self):
    #     if QMessageBox.question(self.widget(), "",
    #                             tr("HallEffect", "Reset all settings to default values?"),
    #                             QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
    #         self.keyboard.hall_effect_reset()
    #         self.reload_settings()

    def update_mode(self, mode):
        self.mode.setChecked(mode) 
        self.sensitivity.setEnabled(mode)
        self.txt_sensitivity.setEnabled(mode)
        self.lbl_sensitivity.setEnabled(mode)

    def update_sensitivity(self, sensitivity):
        self.sensitivity.setSliderPosition(int(sensitivity))
        self.txt_sensitivity.setText(f'{sensitivity*0.05:.2f} mm')

    def update_travel_dist(self, dist):
        self.travel_dist.setCurrentText(f'{dist:.1f} mm')
        self.actuation.setMaximum(int(dist*10 - 1))

    def update_actuation(self, actuation):
        self.actuation.setSliderPosition(int(actuation))
        self.txt_actuation.setText(f'{actuation/10:.1f} mm')

    def on_mode_changed(self, mode):
        if mode == 2:
            mode = 1
        self.val_mode = mode
        self.sensitivity.setEnabled(mode)
        self.txt_sensitivity.setEnabled(mode)
        self.lbl_sensitivity.setEnabled(mode)
        
        self.on_change()

    def on_sensitivity_changed(self, sensitivity):
        self.val_sensitivity = sensitivity*5
        self.txt_sensitivity.setText(f'{sensitivity*0.05:.2f} mm')
        
        self.on_change()

    def on_travel_dist_changed(self, dist):
        travel_dist = 0
        if dist == "3.5 mm":
            travel_dist = 350
        elif dist == "4.0 mm":
            travel_dist = 400
        
        self.actuation.setMaximum(int(travel_dist/10 - 1))
        
        self.val_travel_dist = travel_dist

        self.on_change()

    def on_actuation_changed(self, actuation):
        self.val_actuation = actuation * 10
        self.txt_actuation.setText(f'{actuation/10:.1f} mm')

        self.on_change()
        
    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
                (self.device.keyboard and self.device.keyboard.key_settings != -1)