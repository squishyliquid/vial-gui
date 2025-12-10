# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QGridLayout, QLabel, QSlider, \
   QComboBox, QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QGroupBox, QStackedWidget, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTabWidget

from editor.basic_editor import BasicEditor
from widgets.keyboard_widget_he import KeyboardWidgetHE
from widgets.square_button import SquareButton
# from keycodes.keycodes import Keycode
from util import tr, KeycodeDisplay
from vial_device import VialKeyboard

from PyQt5.QtWidgets import QWidget, QFrame, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt5.QtCore import Qt, QRectF, QPoint

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # if self.orientation() == Qt.Horizontal:
            #     ratio = event.x() / self.width()
            # else:  # vertical
            #     ratio = event.y() / self.height()

            if self.orientation() == Qt.Horizontal:
                # Subtract half the handle width (6 px)
                pos = event.x() - 6
                ratio = pos / (self.width() - 12)
            else:  # vertical
                # Subtract half the handle height (6 px)
                pos = event.y() - 6
                ratio = pos / (self.height() - 12)

            ratio = max(0, min(1, ratio))

            # Adjust ratio based on inverted appearance
            if self.invertedAppearance() != (self.orientation() == Qt.Vertical):
                ratio = 1 - ratio

            value = round(self.minimum() + ratio * (self.maximum() - self.minimum()))
            self.setValue(value)
            event.accept()
        super().mousePressEvent(event)

class SwitchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(55, 70)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Scale to better fit the widget
        painter.scale(0.75, 1.0)
        # painter.scale(0.37, 0.5)

        # Background
        # painter.fillRect(self.rect(), QColor("#FFFFFF"))

        # Keycap (top, gray outline)
        # keycap_rect = QRectF(50, 20, 100, 50)
        # painter.setBrush(Qt.NoBrush)
        # painter.setPen(QPen(QColor("#7c7c7c"), 5))
        # painter.drawRoundedRect(keycap_rect, 8, 8)

        #stem_colors = ["#00aaff", "#0088cc", "#00aaff"] 116AAA

        # Stem (3 blue rectangles)
        stem_colors = ["#1685D4", "#1A9FFF", "#1685D4"]
        stem_rects = [QRectF(22, 0, 9, 14),
                      QRectF(33, 0, 9, 16),
                      QRectF(44, 0, 9, 14)]
        for rect, color in zip(stem_rects, stem_colors):
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7c7c7c"), 2))
        points = QPolygon([
            QPoint(11, 16),    # top-left
            QPoint(64, 16),   # top-right
            QPoint(73, 36),  # bottom-right
            QPoint(2, 36)     # bottom-left
        ])
        painter.drawPolygon(points)

        painter.setBrush(QBrush(QColor("#1A9FFF")))
        painter.setPen(Qt.NoPen)
        points = QPolygon([
            QPoint(16, 19),    # top-left
            QPoint(59, 19),   # top-right
            QPoint(62, 33),  # bottom-right
            QPoint(13, 33)     # bottom-left
        ])
        painter.drawPolygon(points)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7c7c7c"), 2))
        painter.drawRect(QRectF(0, 36, 75, 4))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7c7c7c"), 2))
        points = QPolygon([
            QPoint(2, 40),    # top-left
            QPoint(73, 40),   # top-right
            QPoint(67, 60),  # bottom-right
            QPoint(8, 60)     # bottom-left
        ])
        painter.drawPolygon(points)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7c7c7c"), 2))
        painter.drawRect(QRectF(11, 60, 2, 10))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#7c7c7c"), 2))
        painter.drawRect(QRectF(62, 60, 2, 10))

class ClickableWidget(QWidget):

    clicked = pyqtSignal()

    def mousePressEvent(self, evt):
        super().mousePressEvent(evt)
        self.clicked.emit()

class HallEffect(BasicEditor):
    def __init__(self, layout_editor):
        super().__init__()
        self.layout_editor = layout_editor

        # --- Keyboard container ---
        self.container = KeyboardWidgetHE(layout_editor)
        self.container.clicked.connect(self.on_key_clicked)
        self.container.deselected.connect(self.on_key_deselected)

        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(self.container)
        main_layout.addStretch()
        main_layout.setAlignment(self.container, Qt.AlignHCenter)

        empty_space_widget = ClickableWidget()
        empty_space_widget.setLayout(main_layout)
        empty_space_widget.clicked.connect(self.on_empty_space_clicked)
        self.addWidget(empty_space_widget)

        #
        # --- Settings Section ---
        #
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(0)
        settings_widget.setLayout(settings_layout)

        # buttons
        self.buttons = QWidget()
        self.button_layout = QHBoxLayout()
        # button_layout.addStretch()
        self.buttons.setLayout(self.button_layout)
        self.buttons.setFixedHeight(40)
        self.layer_buttons = []
        # self.container.current_layer = 0
        
        #
        # --- Tab Widget ---
        #
        self.tab_widget = QTabWidget()
        # tab_widget.setFixedWidth(700)
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.setTabPosition(QTabWidget.South)

        #
        # --- Tab 1: General ---
        #
        tab_general = QWidget()
        tab_general_layout = QHBoxLayout(tab_general)
        tab_general_layout.setContentsMargins(10, 10, 10, 10)  # margins around the tab
        tab_general_layout.setSpacing(20)  # space between columns

        # Total Travel
        self.total_travel_lbl = QLabel(tr("HallEffect", "Total Travel"))
        self.total_travel_cmb = QComboBox()
        # self.total_travel_cmb.addItems(["3.2 mm", "3.4 mm", "3.5 mm", "3.8 mm", "3.9 mm"])
        self.total_travel_cmb.currentTextChanged.connect(self.on_total_travel_changed)

        # Special Layer
        self.special_layer_lbl = QLabel(tr("HallEffect", "2nd config layer"))
        self.special_layer_cmb = QComboBox()
        # self.special_layer_cmb.addItems(["None"])
        self.special_layer_cmb.currentTextChanged.connect(self.on_special_layer_changed)

        general_settings_grid = QGridLayout()
        general_settings_grid.setContentsMargins(0, 0, 0, 0)
        general_settings_grid.setSpacing(10)

        general_settings_grid.addWidget(self.total_travel_lbl, 0, 0, 1, 2)
        general_settings_grid.addWidget(self.total_travel_cmb, 0, 2, 1, 2)

        general_settings_grid.addWidget(self.special_layer_lbl, 5, 0, 1, 2)
        general_settings_grid.addWidget(self.special_layer_cmb, 5, 2, 1, 2)

        general_settings_grid.setRowMinimumHeight(2, 20) 

        # Wrap grid in a QWidget
        general_settings_widget = QWidget()
        general_settings_widget.setLayout(general_settings_grid)
        general_settings_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # general_settings_widget.setFixedHeight(60)
        general_settings_widget.setFixedWidth(250)

        # --- Wrap in a QGroupBox to get the section look ---
        general_group_box = QGroupBox("")  # optional title
        # general_group_box.setFixedWidth(240)  
        # general_group_box.setFixedHeight(240)  
        general_group_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        general_rt_group_layout_1 = QVBoxLayout(general_group_box)
        general_rt_group_layout_1.setContentsMargins(20, 20, 20, 20)
        general_rt_group_layout_1.setAlignment(Qt.AlignTop)
        general_rt_group_layout_1.addWidget(general_settings_widget)

        general_group_box.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        tab_general_layout.addWidget(general_group_box)

        #
        # --- Tab 2: Actuation Point ---
        #
        tab_actuation = QWidget()
        tab_actuation_layout = QHBoxLayout(tab_actuation)
        tab_actuation_layout.setContentsMargins(10, 10, 10, 10)  # margins around the tab
        tab_actuation_layout.setSpacing(20)  # space between columns

        # Actuation point

        switch = SwitchWidget()

        self.actuation_lbl = QLabel(tr("HallEffect", "Set actuation point: "))
        self.actuation_sld = ClickableSlider(Qt.Vertical)
        self.actuation_sld.setInvertedAppearance(True)
        self.actuation_sld.setMinimum(1)
        self.actuation_sld.valueChanged.connect(self.on_actuation_sld_changed)
        self.actuation_sld.sliderReleased.connect(self.on_actuation_sld_released)
        self.actuation_txt = QLabel()

        # 00AEEF
        self.actuation_sld.setStyleSheet("""
            QSlider {
                background: transparent;
            }

            QSlider::groove:vertical {
                border: none;
                width: 3px;
                background: #666;
                border-radius: 1px;
            }
            QSlider::sub-page:vertical {
                background: #1A9FFF;
                border-radius: 1px;
            }
            QSlider::add-page:vertical {
                background: #454545;
                border-radius: 1px;
            }
            QSlider::handle:vertical {
                background: white;
                border: none;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: 0px -5px;
            }
        """)

        actuation_settings_grid = QGridLayout()
        actuation_settings_grid.setContentsMargins(0, 0, 0, 0)
        actuation_settings_grid.setSpacing(10)

        actuation_settings_grid.addWidget(self.actuation_lbl, 0, 0, 1, 4)
        actuation_settings_grid.addWidget(switch, 1, 0, 5, 2, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        actuation_settings_grid.addWidget(self.actuation_sld, 2, 2, 3, 1)
        actuation_settings_grid.addWidget(self.actuation_txt, 3, 3, 1, 1)

        # Wrap grid in a QWidget
        actuation_settings_widget = QWidget()
        actuation_settings_widget.setLayout(actuation_settings_grid)
        actuation_settings_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        actuation_settings_widget.setFixedHeight(200)
        actuation_settings_widget.setFixedWidth(250)

        # --- Wrap in a QGroupBox to get the section look ---
        actuation_group_box = QGroupBox("")  # optional title
        # actuation_group_box.setFixedWidth(240)  # enough to include contents + margins
        # actuation_group_box.setFixedHeight(240)  # optional
        actuation_group_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        actuation_rt_group_layout_1 = QVBoxLayout(actuation_group_box)
        actuation_rt_group_layout_1.setContentsMargins(20, 20, 20, 20)
        actuation_rt_group_layout_1.setAlignment(Qt.AlignTop)  
        actuation_rt_group_layout_1.addWidget(actuation_settings_widget)

        actuation_group_box.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        tab_actuation_layout.addWidget(actuation_group_box)

        #
        # --- Tab 3: Rapid Trigger ---
        #
        tab_rapid_trigger = QWidget()
        rapid_trigger_layout = QHBoxLayout(tab_rapid_trigger)
        rapid_trigger_layout.setContentsMargins(10, 10, 10, 10)  # margins around the tab
        rapid_trigger_layout.setSpacing(20)  # space between columns

        # Rapid Trigger
        self.rt_cbx = QCheckBox("Rapid Trigger")
        self.rt_cbx.stateChanged.connect(self.on_rt_changed)

        # Continuous Rapid Trigger
        self.crt_cbx = QCheckBox("Continuous Rapid Trigger")
        self.crt_cbx.stateChanged.connect(self.on_crt_changed)
        
        rt_grid_1 = QGridLayout()
        rt_grid_1.setContentsMargins(0, 0, 0, 0)
        # rt_grid_1.setContentsMargins(20, 0, 0, 0)
        rt_grid_1.setSpacing(10)

        rt_grid_1.addWidget(self.rt_cbx, 0, 0, 1, 2)
        rt_grid_1.addWidget(self.crt_cbx, 1, 0, 1, 3)

        # Wrap grid in a QWidget
        rt_settings_1 = QWidget()
        rt_settings_1.setLayout(rt_grid_1)
        rt_settings_1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rt_settings_1.setFixedHeight(40)
        rt_settings_1.setFixedWidth(250)

        # --- Wrap in a QGroupBox to get the section look ---
        rt_group_1 = QGroupBox("")  # optional title
        rt_group_layout_1 = QVBoxLayout(rt_group_1)
        rt_group_layout_1.setContentsMargins(20, 20, 20, 20)
        rt_group_layout_1.setAlignment(Qt.AlignTop)  
        rt_group_layout_1.addWidget(rt_settings_1)

        rt_group_1.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        rapid_trigger_layout.addWidget(rt_group_1)

        # Sensitivity
        self.rt_separate_cbx = QCheckBox("Separate Press/Release Sensitivity")
        self.rt_separate_cbx.stateChanged.connect(self.on_rt_separate_changed)

        self.rt_press_lbl = QLabel(tr("HallEffect", "Sensitivity"))
        self.rt_press_sld = ClickableSlider(Qt.Horizontal)
        self.rt_press_sld.setRange(2, 20)
        self.rt_press_sld.valueChanged.connect(self.on_rt_press_sld_changed)
        self.rt_press_sld.sliderReleased.connect(self.on_rt_press_sld_released)
        self.rt_press_txt = QLabel()
        self.rt_press_high_lbl = QLabel(tr("HallEffect", "High"))
        self.rt_press_low_lbl = QLabel(tr("HallEffect", "Low"))

        self.rt_press_sld.setStyleSheet("""
            QSlider {
                background: transparent;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 3px;
                background: #666;
                border-radius: 1px;
            }
            QSlider::sub-page:horizontal {
                background: #1A9FFF;
                border-radius: 1px;
            }
            QSlider::add-page:horizontal {
                background: #454545;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: none;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -5px 0;
            }
        """)

        self.rt_release_lbl = QLabel(tr("HallEffect", "Release Sensitivity"))
        self.rt_release_sld = ClickableSlider(Qt.Horizontal)
        self.rt_release_sld.setRange(2, 20)
        self.rt_release_sld.valueChanged.connect(self.on_rt_release_sld_changed)
        self.rt_release_sld.sliderReleased.connect(self.on_rt_release_sld_released)
        self.rt_release_txt = QLabel()
        self.rt_release_high_lbl = QLabel(tr("HallEffect", "High"))
        self.rt_release_low_lbl = QLabel(tr("HallEffect", "Low"))

        self.rt_release_sld.setStyleSheet("""
            QSlider {
                background: transparent;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 3px;
                background: #666;
                border-radius: 1px;
            }
            QSlider::sub-page:horizontal {
                background: #1A9FFF;
                border-radius: 1px;
            }
            QSlider::add-page:horizontal {
                background: #454545;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: none;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -5px 0;
            }
        """)

        rt_grid_2 = QGridLayout()
        rt_grid_2.setContentsMargins(0, 0, 0, 0)
        # rt_grid_2.setContentsMargins(0, 0, 20, 0)
        rt_grid_2.setSpacing(10)

        rt_grid_2.addWidget(self.rt_separate_cbx, 0, 0, 1, 4)

        rt_grid_2.addWidget(self.rt_press_lbl, 2, 0, 1, 3)
        rt_grid_2.addWidget(self.rt_press_sld, 3, 0, 1, 3)
        rt_grid_2.addWidget(self.rt_press_txt, 3, 3)
        rt_grid_2.addWidget(self.rt_press_high_lbl, 4, 0)
        rt_grid_2.addWidget(self.rt_press_low_lbl, 4, 2, alignment=Qt.AlignRight)

        rt_grid_2.addWidget(self.rt_release_lbl, 6, 0, 1, 3)
        rt_grid_2.addWidget(self.rt_release_sld, 7, 0, 1, 3)
        rt_grid_2.addWidget(self.rt_release_txt, 7, 3)
        rt_grid_2.addWidget(self.rt_release_high_lbl, 8, 0)
        rt_grid_2.addWidget(self.rt_release_low_lbl, 8, 2, alignment=Qt.AlignRight)

        rt_grid_2.setRowMinimumHeight(1, 20)
        rt_grid_2.setRowMinimumHeight(5, 20)

        # Wrap grid in a QWidget
        rt_settings_2 = QWidget()
        rt_settings_2.setLayout(rt_grid_2)
        rt_settings_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # rt_settings_2.setFixedHeight(60)
        rt_settings_2.setFixedWidth(250)

        # --- Wrap in a QGroupBox to get the section look ---
        rt_group_2 = QGroupBox("")  # optional title
        rt_group_layout_2 = QVBoxLayout(rt_group_2)
        rt_group_layout_2.setContentsMargins(20, 20, 20, 20)
        rt_group_layout_2.setAlignment(Qt.AlignTop)  
        rt_group_layout_2.addWidget(rt_settings_2)

        rt_group_2.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        rapid_trigger_layout.addWidget(rt_group_2)

        #
        # --- Tab 4: Advanced Keys ---
        #
        tab_advanced_keys = QWidget()
        tab_advanced_layout = QHBoxLayout(tab_advanced_keys)
        tab_advanced_layout.setContentsMargins(10, 10, 10, 10)  # margins around the tab
        tab_advanced_layout.setSpacing(20)  # space between columns

        # Create stacked widget
        self.ak_stack = QStackedWidget()
        tab_advanced_layout.addWidget(self.ak_stack)

        # --- Page 1: default layout ---
        self.ak_overview = QWidget()
        ak_overview_layout = QHBoxLayout(self.ak_overview)
        ak_overview_layout.setContentsMargins(0, 0, 0, 0)
        ak_overview_layout.setSpacing(20)
        
        self.ak_stack.addWidget(self.ak_overview)

        ak_option_grid = QGridLayout()
        ak_option_grid.setContentsMargins(0, 0, 0, 0)
        ak_option_grid.setSpacing(10)

        lbl = QLabel("Add Advanced Keys")
        ak_option_grid.addWidget(lbl, 0, 0)

        self.input_priority_btn = QPushButton("Input Priority")
        self.input_priority_btn.clicked.connect(self.on_input_priority_btn_clicked)
        ak_option_grid.addWidget(self.input_priority_btn, 1, 0)

        # Wrap grid in a QWidget
        ak_option = QWidget()
        ak_option.setLayout(ak_option_grid)
        ak_option.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # ak_option.setFixedHeight(40)
        ak_option.setFixedWidth(150)

        # --- Wrap in a QGroupBox to get the section look ---
        ak_option_group = QGroupBox("")  # optional title
        ak_option_layout = QVBoxLayout(ak_option_group)
        ak_option_layout.setContentsMargins(20, 20, 20, 20)
        ak_option_layout.setAlignment(Qt.AlignTop)  
        ak_option_layout.addWidget(ak_option)

        ak_option_group.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        ak_overview_layout.addWidget(ak_option_group)

        # This replaces your QGridLayout
        self.container.ak_list_layout = QVBoxLayout()
        self.container.ak_list_layout.setContentsMargins(0, 0, 0, 0)
        self.container.ak_list_layout.setSpacing(10)

        # Title (not scrollable)
        self.ak_title_lbl = QLabel("Active Advanced Keys")
        self.ak_title_lbl.setAlignment(Qt.AlignLeft)
        self.container.ak_list_layout.addWidget(self.ak_title_lbl)

        # Scroll area
        self.ak_scroll = QScrollArea()
        self.ak_scroll.setWidgetResizable(True)
        self.ak_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.ak_scroll.setViewportMargins(0, 0, 20, 0)
        self.ak_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ak_scroll.setFrameShape(QScrollArea.NoFrame)   # remove outline

        self.ak_scroll.setStyleSheet("""
        QScrollBar:vertical {
            background: transparent;
            width: 4px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: #454545;
            border-radius: 2px;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """)

        # Content widget inside scroll area
        self.ak_scroll_content = QWidget()
        self.ak_scroll_layout = QVBoxLayout(self.ak_scroll_content)
        self.ak_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.ak_scroll_layout.setSpacing(12)
        self.ak_scroll_layout.setAlignment(Qt.AlignTop)

        # add content to scroll area
        self.ak_scroll.setWidget(self.ak_scroll_content)

        self.container.ak_list_layout.addWidget(self.ak_scroll)

        ak_list_group = QGroupBox("")
        ak_list_group.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        group_layout = QVBoxLayout(ak_list_group)
        group_layout.setContentsMargins(20, 20, 20, 20)
        group_layout.addLayout(self.container.ak_list_layout)

        ak_overview_layout.addWidget(ak_list_group)

        # --- Page 2 ---
        self.input_priority_page = QWidget()
        input_priority_page_layout = QHBoxLayout(self.input_priority_page)
        input_priority_page_layout.setContentsMargins(0, 0, 0, 0)
        input_priority_page_layout.setSpacing(20)
        
        self.ak_stack.addWidget(self.input_priority_page)

        ak_grid_1 = QGridLayout()
        ak_grid_1.setContentsMargins(0, 0, 0, 0)
        ak_grid_1.setSpacing(10)

        # Wrap grid in a QWidget
        ak_settings_1 = QWidget()
        ak_settings_1.setLayout(ak_grid_1)
        ak_settings_1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # ak_settings_1.setFixedHeight(350)
        ak_settings_1.setFixedWidth(250)

        # --- Wrap in a QGroupBox to get the section look ---
        ak_group_1 = QGroupBox("")  # optional title
        ak_group_1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        ak_group_layout_1 = QVBoxLayout(ak_group_1)
        ak_group_layout_1.setContentsMargins(20, 20, 20, 20)
        ak_group_layout_1.setAlignment(Qt.AlignTop)  
        ak_group_layout_1.addWidget(ak_settings_1)

        ak_group_1.setStyleSheet("""
            QGroupBox {
                background-color: #353535;
                border-radius: 8px;
            }
        """)

        # tab_advanced_layout.addWidget(ak_group_1)
        input_priority_page_layout.addWidget(ak_group_1)

        # # --- Left column ---

        self.key_1 = QPushButton("")
        self.key_1.setFixedSize(50, 50)
        self.key_1.setCheckable(True)
        self.key_1.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #454545;
                border-radius: 10px;
            }
            QPushButton:checked {
                border: 2px solid #7c7c7c;
            }
        """)

        ak_grid_1.addWidget(self.key_1, 0, 0, 1, 1)

        self.key_2 = QPushButton("")
        self.key_2.setFixedSize(50, 50)
        self.key_2.setCheckable(True)
        self.key_2.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #454545;
                border-radius: 10px;
            }
            QPushButton:checked {
                border: 2px solid #7c7c7c;
            }
        """)
        ak_grid_1.addWidget(self.key_2, 0, 1, 1, 1)

        lbl1 = QLabel("Key 1")
        lbl1.setAlignment(Qt.AlignCenter)
        lbl1.setStyleSheet("color: #1A9FFF;")
        # lbl1.setStyleSheet("font-size: 11px;")
        ak_grid_1.addWidget(lbl1, 1, 0, alignment=Qt.AlignBottom)

        lbl2 = QLabel("Key 2")
        lbl2.setAlignment(Qt.AlignCenter)
        lbl2.setStyleSheet("color: #1A9FFF;")
        # lbl2.setStyleSheet("font-size: 11px;")
        ak_grid_1.addWidget(lbl2, 1, 1, alignment=Qt.AlignBottom)

        self.input_priority_group = QButtonGroup()
        self.input_priority_group.addButton(self.key_1)
        self.input_priority_group.addButton(self.key_2)
        self.input_priority_group.setExclusive(True)

        self.key_1.setProperty("slot_index", 0)
        self.key_2.setProperty("slot_index", 1)
        self.key_1.setCheckable(False)
        self.key_2.setCheckable(False)

        for b in self.input_priority_group.buttons():
            b.pressed.connect(lambda b=b: self.on_input_priority_key_select(b))

        option1 = QRadioButton("Last Priority")
        option2 = QRadioButton("Absolute Priority (Key 1)")
        option3 = QRadioButton("Absolute Priority (Key 2)")
        option4 = QRadioButton("Neutral")
        option5 = QRadioButton("Depth Priority")

        self.input_priority_resolution_group = QButtonGroup()
        self.input_priority_resolution_group.addButton(option1, 0)
        self.input_priority_resolution_group.addButton(option2, 1)
        self.input_priority_resolution_group.addButton(option3, 2)
        self.input_priority_resolution_group.addButton(option4, 3)
        self.input_priority_resolution_group.addButton(option5, 4)

        for b in self.input_priority_resolution_group.buttons():
            b.pressed.connect(lambda b=b: self.on_input_priority_resolution_pressed(b))

        option1.setChecked(True)

        ak_grid_1.addWidget(option1, 2, 0, 1, 3)
        ak_grid_1.addWidget(option2, 3, 0, 1, 3)
        ak_grid_1.addWidget(option3, 4, 0, 1, 3)
        ak_grid_1.addWidget(option4, 5, 0, 1, 3)
        ak_grid_1.addWidget(option5, 6, 0, 1, 3)

        ak_grid_1.setRowMinimumHeight(1, 20) 

        #
        # --- Add Tabs ---
        #
        self.tab_widget.addTab(tab_general, tr("HallEffect", "General"))
        self.tab_widget.addTab(tab_actuation, tr("HallEffect", "Actuation Point"))
        self.tab_widget.addTab(tab_rapid_trigger, tr("HallEffect", "Rapid Trigger"))
        self.tab_widget.addTab(tab_advanced_keys, tr("HallEffect", "Advanced Keys"))

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setCurrentIndex(0)
        # self.on_tab_changed(0)

        #
        # --- Tab Style ---
        #
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border-radius: 16px;
                border: none;
                margin-bottom: 20px;
            }
            QTabBar::tab {
                background: transparent;
                color: white;
                border-radius: 12px;
                padding: 8px 12px;
                margin: 4px 0;
                min-width: 100px;
                max-width: 100px; /* all tabs the same width */
            }
            QTabBar::tab:first { 
                margin-left: 4px;
            } 
            QTabBar::tab:last {
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1A9FFF;
                color: white;
            }
            QTabBar {
                background-color: #353535;
                border-radius: 16px;
                margin: 0px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)

        #
        # --- Combine settings ---
        #
        self.hint_txt = QLabel("")
        self.hint_txt.setFixedHeight(40)
        self.hint_txt.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        settings_layout.addWidget(self.hint_txt)
        settings_layout.addWidget(self.buttons)
        settings_layout.addWidget(self.tab_widget)

        empty_space = ClickableWidget()
        empty_space_layout = QVBoxLayout(empty_space)
        empty_space_layout.addWidget(settings_widget, alignment=Qt.AlignHCenter)
        empty_space_layout.addStretch()

        self.addWidget(empty_space)

    def on_total_travel_changed(self, dist):
        prev_switch = self.switch_display_val

        self.switch_display_val = self.total_travel_cmb.currentIndex()
        total_travel = self.total_travel[self.switch_display_val]

        last_row, last_col = self.container.last_key.desc.row, self.container.last_key.desc.col
        
        for widget in self.container.widgets:
            row = widget.desc.row
            col = widget.desc.col
            
            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            # new value in mm
            actuation_point = min(self.convert_to_nearest_10mm(actuation.actuation_point), total_travel - 10)
            rt_press = self.convert_to_nearest_5mm(actuation.rt_press, prev_switch)
            rt_release = self.convert_to_nearest_5mm(actuation.rt_release, prev_switch)

            # new value in 255
            actuation.actuation_point = self.convert_to_255(actuation_point)
            actuation.rt_press = self.convert_to_255(rt_press)
            actuation.rt_release = self.convert_to_255(rt_release)

            self.keyboard.set_actuation_config(self.profile, row, col)

            if row == last_row and col == last_col:
                self.actuation_display_val = actuation_point
                self.rt_press_display_val = rt_press
                self.rt_release_display_val = rt_release

                self.refresh_settings_display()

        self.total_travel_val = total_travel
        
        self.keyboard.switch_option = self.switch_display_val
        self.keyboard.set_switch_option()

        # print(f"Total Travel: {total_travel}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_special_layer_changed(self, layer):

        if self.special_layer_cmb.currentIndex() == 0:
            self.keyboard.reset_actuation_profile(1)
            print("RESET 2nd PROFILE")

        self.profile = (self.special_layer_cmb.currentIndex() - 1 == self.container.current_layer)

        self.special_layer_display_val = self.special_layer_cmb.currentIndex()

        self.keyboard.special_layer = self.special_layer_display_val
        self.keyboard.set_special_layer()

        # print(f"2nd config layer: {self.special_layer_display_val}") 

        self.refresh_layout_display()

    def on_actuation_sld_changed(self, actuation):
        # self.val_actuation = actuation * 10
        self.actuation_display_val = actuation * 10
        self.actuation_txt.setText(f'{actuation / 10:.1f} mm')
        
        self.temp_actuation_display()

    def on_actuation_sld_released(self):
        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]
            actuation.actuation_point = self.convert_to_255(self.actuation_display_val)
            self.keyboard.set_actuation_config(self.profile, row, col)

            # print(f"Set actuation point: {actuation.actuation_point}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_rt_changed(self, mode):
        if mode == 2:
            mode = 1

        if mode == 0:
            self.rt_separate_val = 0
            self.rt_press_display_val = 0
        
        elif mode == 1:
            self.rt_press_display_val = 20

        self.rt_mode_display_val = mode

        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col
            
            actuation = self.keyboard.actuation_matrix[self.profile][row][col]
            actuation.rt_mode = mode

            if mode == 0:
                actuation.rt_press = 0
                actuation.rt_release = 0
            
            elif mode == 1:
                actuation.rt_press = self.convert_to_255(20)

            self.keyboard.set_actuation_config(self.profile, row, col)
            
            # print(f"Set Mode: {self.rt_mode_display_val}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_crt_changed(self, mode):
        if mode == 0:
            mode = 1

        if self.rt_mode_display_val != 0:
            self.rt_mode_display_val = mode

        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col
            
            actuation = self.keyboard.actuation_matrix[self.profile][row][col]
            actuation.rt_mode = mode
            self.keyboard.set_actuation_config(self.profile, row, col)

            # print(f"Set Mode: {self.rt_mode_display_val}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_rt_separate_changed(self, separate):
        self.rt_separate_val = separate

        if separate:
            self.rt_press_lbl.setText("Press Sensitivity")
            self.rt_release_display_val = 20
        else:
            self.rt_press_lbl.setText("Sensitivity")
            self.rt_release_display_val = 0

        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            actuation.rt_mode = self.rt_mode_display_val

            if separate:
                actuation.rt_release = self.convert_to_255(20)
            else:
                actuation.rt_release = 0

            self.keyboard.set_actuation_config(self.profile, row, col)

            # print(f"Separate sens: {self.rt_mode_display_val}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_rt_press_sld_changed(self, press):
        self.rt_press_display_val = press * 5
        self.rt_press_txt.setText(f'{press * 0.05:.2f} mm')

        self.temp_rt_press_display()

    def on_rt_press_sld_released(self):
        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]
            actuation.rt_mode = self.rt_mode_display_val
            actuation.rt_press = self.convert_to_255(self.rt_press_display_val)

            self.keyboard.set_actuation_config(self.profile, row, col)

            # print(f"Set press sens: {actuation.rt_mode, actuation.rt_press}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_rt_release_sld_changed(self, release):
        self.rt_release_display_val = release * 5
        self.rt_release_txt.setText(f'{release * 0.05:.2f} mm')

        self.temp_rt_release_display()

    def on_rt_release_sld_released(self):
        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]
            actuation.rt_mode = self.rt_mode_display_val
            actuation.rt_release = self.convert_to_255(self.rt_release_display_val)

            self.keyboard.set_actuation_config(self.profile, row, col)

            # print(f"Set release sens: {actuation.rt_mode, actuation.rt_release}")

        self.refresh_layout_display()
        self.refresh_settings_display()

    def on_input_priority_key_select(self, button):
        idx = button.property("slot_index")
        self.container.input_priority_index = idx
        self.container.input_priority_pair[idx] = None

        self.refresh_input_priority_display()

    def on_input_priority_resolution_pressed(self, idx):
        self.input_priority_resolution = self.input_priority_resolution_group.id(idx)
        # print(self.input_priority_resolution_group.id(idx))

    def on_input_priority_done_btn_clicked(self):
        self.ak_stack.setCurrentWidget(self.ak_overview)
    
        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(idx != self.container.current_layer)

        self.input_priority_cancel_btn.setVisible(False)
        self.input_priority_done_btn.setVisible(False)

        input_priority_pair = (
            self.container.current_layer,
            self.container.input_priority_pair[0].desc.row,
            self.container.input_priority_pair[0].desc.col,
            self.container.input_priority_pair[1].desc.row,
            self.container.input_priority_pair[1].desc.col,
            self.input_priority_resolution
        )

        if self.edit_pair is None:
            self.keyboard.input_priority_pairs.append(input_priority_pair)
            self.keyboard.set_input_priority_pair(-1)

            self.container.input_priority_pairs.append((self.container.current_layer, self.container.input_priority_pair[0], 
                                                        self.container.input_priority_pair[1], self.input_priority_resolution))
        else:
            self.keyboard.input_priority_pairs[self.edit_pair] = input_priority_pair
            self.keyboard.set_input_priority_pair(self.edit_pair)

            self.container.input_priority_pairs[self.edit_pair] = (self.container.current_layer, self.container.input_priority_pair[0], 
                                                        self.container.input_priority_pair[1], self.input_priority_resolution)
            
            self.edit_pair = None
            self.key_1.setEnabled(True)
            self.key_2.setEnabled(True)

        self.container.select_enabled = False
        self.container.input_priority_index = 0
        self.container.input_priority_pair = [None, None]
        self.input_priority_resolution = 0
        self.input_priority_resolution_group.button(0).setChecked(True)

        self.refresh_layout_display()
        self.refresh_pairs_view()

        # print(self.container.input_priority_pairs)
        # print(self.keyboard.input_priority_pairs)

    def on_input_priority_btn_clicked(self):
        self.refresh_input_priority_display()
        self.ak_stack.setCurrentWidget(self.input_priority_page)
        self.container.select_enabled = True

        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(False)
        
        self.input_priority_cancel_btn.setVisible(True)
        self.input_priority_done_btn.setVisible(True)

    def on_input_priority_edit_btn_clicked(self, pair_idx):
        self.edit_pair = pair_idx
        pair = self.container.input_priority_pairs[pair_idx]
        self.container.input_priority_pair = [pair[1], pair[2]]
        self.container.input_priority_index = None
        self.input_priority_resolution = pair[3]
        self.input_priority_resolution_group.button(pair[3]).setChecked(True)

        self.key_1.setEnabled(False)
        self.key_2.setEnabled(False)

        self.switch_layer(pair[0])

        self.refresh_input_priority_display()
        self.ak_stack.setCurrentWidget(self.input_priority_page)
        # self.container.select_enabled = True

        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(False)
        
        # self.input_priority_cancel_btn.setVisible(True)
        self.input_priority_done_btn.setVisible(True)

    def on_input_priority_cancel_btn_clicked(self):
        self.ak_stack.setCurrentWidget(self.ak_overview)
    
        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(idx != self.container.current_layer)

        self.input_priority_cancel_btn.setVisible(False)
        self.input_priority_done_btn.setVisible(False)

        self.container.select_enabled = False
        self.container.input_priority_index = 0
        self.container.input_priority_pair = [None, None]
        self.input_priority_resolution = 0
        self.input_priority_resolution_group.button(0).setChecked(True)

        # print(self.container.input_priority_pairs)
        # print(self.keyboard.input_priority_pairs)

    def on_tab_changed(self, index):
        self.container.tab_index = index

        for i in reversed(range(self.keyboard.layers + 2, self.button_layout.count())):
            item = self.button_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if index == 0:
            self.hint_txt.setText("")
            self.container.deselect_all()
            self.container.disable_interaction()

            self.refresh_layout_display()
            return
        
        self.container.enable_interaction()

        if index == 3:
            self.hint_txt.setText("")
            self.container.deselect_all()
            
            self.input_priority_cancel_btn = QPushButton(tr("HallEffect", "Cancel"))
            self.input_priority_cancel_btn.clicked.connect(self.on_input_priority_cancel_btn_clicked)
            self.button_layout.addWidget(self.input_priority_cancel_btn)
            
            self.input_priority_done_btn = QPushButton(tr("HallEffect", "Done"))
            self.input_priority_done_btn.clicked.connect(self.on_input_priority_done_btn_clicked)
            self.button_layout.addWidget(self.input_priority_done_btn)

            self.input_priority_cancel_btn.setVisible(False)
            self.input_priority_done_btn.setVisible(False)

            self.refresh_layout_display()
            return
        
        self.hint_txt.setText("Hold [Ctrl] to select multiple keys")

        self.btn_select_all = QPushButton(tr("HallEffect", "Select all keys"))
        self.btn_select_all.clicked.connect(self.on_select_all)
        self.button_layout.addWidget(self.btn_select_all)

        self.btn_discard_all = QPushButton(tr("HallEffect", "Discard selection"))
        self.btn_discard_all.clicked.connect(self.on_discard_all)
        self.button_layout.addWidget(self.btn_discard_all)

        self.refresh_layout_display()

    def text_for_widget(self, widget, layer):
        if widget.desc.row is not None:
            code = self.keyboard.layout[(layer, widget.desc.row, widget.desc.col)]
        else:
            code = self.keyboard.encoder_layout[(layer, widget.desc.encoder_idx,
                                                 widget.desc.encoder_dir)]

        return KeycodeDisplay.get_label(code)
    
    def convert_to_nearest_5mm(self, val, switch_option):
        calculated_value = val / 255 * self.total_travel[switch_option]
        rounded_value = round(calculated_value / 5) * 5
    
        return int(rounded_value)
    
    def convert_to_nearest_10mm(self, val):
        return int(round(val / 255 * self.total_travel[self.switch_display_val], -1))
    
    def convert_to_255(self, val):
        return int(round(val / self.total_travel[self.switch_display_val] * 255))

    def switch_layer(self, idx):
        self.container.deselect()
        self.container.current_layer = idx

        profile_changed = False

        if idx != self.special_layer_display_val - 1 and self.profile == 1:
            self.profile = 0
            profile_changed = True
        elif idx == self.special_layer_display_val - 1 and self.profile == 0:
            self.profile = 1
            profile_changed = True

        if profile_changed:
            # print(self.profile)

            row, col = self.container.last_key.desc.row, self.container.last_key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            self.actuation_display_val = self.convert_to_nearest_10mm(actuation.actuation_point)
            self.rt_mode_display_val = actuation.rt_mode
            self.rt_press_display_val = self.convert_to_nearest_5mm(actuation.rt_press, self.switch_display_val)
            self.rt_release_display_val = self.convert_to_nearest_5mm(actuation.rt_release, self.switch_display_val)

            self.rt_separate_val = 0 if (self.rt_release_display_val == 0) else 2

            self.refresh_settings_display()

        self.refresh_layout_display()

    def refresh_input_priority_display(self):
        buttons = self.input_priority_group.buttons()

        for b in buttons:
            idx = b.property("slot_index")

            txt = "" if self.container.input_priority_pair[idx] is None else self.text_for_widget(self.container.input_priority_pair[idx], self.container.current_layer)

            b.setText(txt)

            if self.container.input_priority_index == idx:
                # SELECTED STYLE
                b.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        border: 2px solid #7c7c7c;
                        border-radius: 8px;
                    }
                """)
            else:
                # UNSELECTED STYLE
                b.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        border: 2px solid #454545;
                        border-radius: 8px;
                    }
                """)
        self.input_priority_done_btn.setEnabled(self.container.input_priority_index == None)
        # print(self.container.input_priority_index)
        self.container.update()

    def refresh_pairs_view(self):

        title = f"Active Advanced Keys ({len(self.container.input_priority_pairs)}/{self.ak_max})"
        self.ak_title_lbl.setText(title)

        self.input_priority_btn.setEnabled(len(self.container.input_priority_pairs) < self.ak_max)

        # Clear old rows
        for i in reversed(range(self.ak_scroll_layout.count())):
            item = self.ak_scroll_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for row_index, pair in enumerate(self.container.input_priority_pairs):

            # Data
            label1 = self.text_for_widget(pair[1], pair[0])
            label2 = self.text_for_widget(pair[2], pair[0])

            # Widgets
            txt1_lbl = QLabel(label1)
            txt2_lbl = QLabel(label2)
            ak_sym  = QLabel(" ⇹") # ↔ ⇹

            resolution_id = pair[3]
            resolution_txt = self.input_priority_resolution_group.button(resolution_id).text()
            if resolution_id == 1:
                resolution_txt = f"Absolute Priority ({label1})"
            elif resolution_id == 2:
                resolution_txt = f"Absolute Priority ({label2})"
            resolution_lbl = QLabel(resolution_txt)

            label_style = """
                QLabel {
                    background-color: #2b2b2b;
                    color: white;
                    border: 2px solid #454545;
                    border-radius: 6px;
                }
            """
            txt1_lbl.setStyleSheet(label_style)
            txt2_lbl.setStyleSheet(label_style)
            txt1_lbl.setFixedSize(40, 40)
            txt2_lbl.setFixedSize(40, 40)
            txt1_lbl.setAlignment(Qt.AlignCenter)
            txt2_lbl.setAlignment(Qt.AlignCenter)

            ak_sym.setStyleSheet("""
                QLabel {
                    padding-bottom: 2px;
                    font-size: 18px;
                }
            """)
            ak_sym.setFixedWidth(24)
            ak_sym.setAlignment(Qt.AlignCenter)
            
            edit_btn = QPushButton("⛮") #◼☰◰🖊️🖌🖊
            edit_btn.setFixedWidth(25)
            edit_btn.setFixedHeight(25)
            edit_btn.setStyleSheet("color: #1A9FFF; font-weight: bold")
            edit_btn.clicked.connect(lambda _, idx=row_index: self.on_input_priority_edit_btn_clicked(idx))

            del_btn = QPushButton("✕")
            del_btn.setFixedWidth(25)
            del_btn.setFixedHeight(25)
            del_btn.setStyleSheet("color: red; font-weight: bold")
            del_btn.clicked.connect(lambda _, idx=row_index: self.delete_pair(idx))

            # Row box
            row_box = QWidget()
            row_box.setFixedWidth(340)

            row_layout = QHBoxLayout(row_box)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)
            row_layout.addWidget(txt1_lbl)
            row_layout.addWidget(txt2_lbl)
            row_layout.addWidget(ak_sym)
            row_layout.addWidget(resolution_lbl)
            row_layout.addWidget(edit_btn)
            row_layout.addWidget(del_btn)

            self.ak_scroll_layout.addWidget(row_box)

    def delete_pair(self, idx):
        if 0 <= idx < len(self.container.input_priority_pairs):
            del self.container.input_priority_pairs[idx]
            del self.keyboard.input_priority_pairs[idx]
            self.keyboard.remove_input_priority_pair(idx)
            self.refresh_pairs_view()
        self.refresh_layout_display()

        # print(self.container.input_priority_pairs)
        # print(self.keyboard.input_priority_pairs)   

    def on_empty_space_clicked(self):
        self.container.deselect_all()
        
    def on_key_clicked(self):
        if self.container.tab_index == 3:
            self.refresh_input_priority_display()
            return
        
        row, col = self.container.last_key.desc.row, self.container.last_key.desc.col

        actuation = self.keyboard.actuation_matrix[self.profile][row][col]

        self.actuation_display_val = self.convert_to_nearest_10mm(actuation.actuation_point)
        self.rt_mode_display_val = actuation.rt_mode
        self.rt_press_display_val = self.convert_to_nearest_5mm(actuation.rt_press, self.switch_display_val)
        self.rt_release_display_val = self.convert_to_nearest_5mm(actuation.rt_release, self.switch_display_val)

        self.rt_separate_val = 0 if (self.rt_release_display_val == 0) else 2

        self.refresh_settings_display()

    def on_key_deselected(self):
        # print("key deselected")
        self.refresh_settings_display()

    def on_select_all(self):
        self.container.select_all()
        self.refresh_settings_display()

    def on_discard_all(self):
        self.container.deselect_all()
        self.refresh_settings_display()

    def temp_actuation_display(self):
        for key in self.container.selected_keys:
            key.setText(f"{self.actuation_display_val / 100:.1f}\n")

        self.container.update()

    def temp_rt_press_display(self):
        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            rt_release = self.convert_to_nearest_5mm(actuation.rt_release, self.switch_display_val)

            key.setState(self.rt_mode_display_val)

            if rt_release != 0:
                key.setText(f"{self.rt_press_display_val / 100:.2f}\n{rt_release / 100:.2f}")
            else:
                key.setText(f"{self.rt_press_display_val / 100:.2f}\n")

        self.container.update()

    def temp_rt_release_display(self):
        for key in self.container.selected_keys:
            row = key.desc.row
            col = key.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            rt_press = self.convert_to_nearest_5mm(actuation.rt_press, self.switch_display_val)

            key.setState(self.rt_mode_display_val)

            key.setText(f"{rt_press / 100:.2f}\n{self.rt_release_display_val / 100:.2f}")

        self.container.update()

    def refresh_general_display(self):
        dist = self.total_travel[self.switch_display_val]

        self.total_travel_cmb.setCurrentText(f'{dist / 100:.1f} mm')
        self.actuation_sld.setMaximum(int(dist / 10 - 1))

        self.special_layer_cmb.setCurrentIndex(self.special_layer_display_val)

    def refresh_actuation_display(self):
        actuation = self.actuation_display_val

        self.actuation_sld.setSliderPosition(int(actuation / 10))
        self.actuation_txt.setText(f'{actuation / 100:.1f} mm')

    def refresh_rt_display(self):
        mode = self.rt_mode_display_val

        self.rt_cbx.setChecked(mode)
        self.rt_cbx.setEnabled(mode)

        self.crt_cbx.setChecked(mode == 2)
        self.crt_cbx.setEnabled(mode)
    
        self.rt_separate_cbx.setChecked(self.rt_separate_val)
        self.rt_press_sld.setSliderPosition(int(self.rt_press_display_val / 5))
        self.rt_press_txt.setText(f'{self.rt_press_display_val * 0.01:.2f} mm')
        self.rt_release_sld.setSliderPosition(int(self.rt_release_display_val / 5))
        self.rt_release_txt.setText(f'{self.rt_release_display_val * 0.01:.2f} mm')
    
    def refresh_settings_display(self):
        for widget in [self.total_travel_cmb, self.special_layer_cmb,
                       self.actuation_sld, 
                       self.rt_cbx, self.crt_cbx, 
                       self.rt_separate_cbx, self.rt_press_sld, self.rt_release_sld]:
            widget.blockSignals(True)

        self.refresh_general_display()
        self.refresh_actuation_display()
        self.refresh_rt_display()
        
        for widget in [self.total_travel_cmb, self.special_layer_cmb,
                       self.actuation_sld, 
                       self.rt_cbx, self.crt_cbx, 
                       self.rt_separate_cbx, self.rt_press_sld, self.rt_release_sld]:
            widget.blockSignals(False)

        if len(self.container.selected_keys) > 0:
            # Disable elements
            for widget in [self.total_travel_lbl, self.total_travel_cmb]:
                widget.setEnabled(False)

            # Enable elements
            for widget in [self.actuation_lbl, self.actuation_txt, self.actuation_sld, self.rt_cbx]:
                widget.setEnabled(True)

            for widget in [self.rt_release_sld, self.rt_release_txt, self.rt_release_lbl, self.rt_release_high_lbl, self.rt_release_low_lbl]:
                widget.setVisible(self.rt_separate_val)

            for widget in [self.crt_cbx, self.rt_separate_cbx,
                           self.rt_press_sld, self.rt_press_txt, self.rt_press_lbl, self.rt_press_high_lbl, self.rt_press_low_lbl,
                           self.rt_release_sld, self.rt_release_txt, self.rt_release_lbl, self.rt_release_high_lbl, self.rt_release_low_lbl]:
                widget.setEnabled(self.rt_mode_display_val)

            # print([(k.desc.row, k.desc.col) for k in self.container.selected_keys])
        else:
            # Enable widgets
            enable_widgets = [self.total_travel_lbl, self.total_travel_cmb]
            for widget in enable_widgets:
                widget.setEnabled(True)
            
            # Disable widgets
            disable_widgets = [self.actuation_lbl, self.actuation_txt, self.actuation_sld, self.rt_cbx, 
                               self.crt_cbx, self.rt_separate_cbx, 
                               self.rt_press_sld, self.rt_press_txt, self.rt_press_lbl, self.rt_press_high_lbl, self.rt_press_low_lbl,
                               self.rt_release_sld, self.rt_release_txt, self.rt_release_lbl, self.rt_release_high_lbl, self.rt_release_low_lbl]
            for widget in disable_widgets:
                widget.setEnabled(False)
            
            for widget in [self.rt_release_sld, self.rt_release_txt, self.rt_release_lbl, self.rt_release_high_lbl, self.rt_release_low_lbl]:
                widget.setVisible(self.rt_separate_val)

    def refresh_layout_display(self):
        index = self.container.tab_index

        special = self.special_layer_display_val - 1

        for idx, btn in enumerate(self.layer_buttons):
            if index in (1, 2):
                enabled = (self.container.current_layer != special and idx == special) or \
                            (self.container.current_layer == special and idx != special)
                checked = (self.container.current_layer == special and idx == special) or \
                            (self.container.current_layer != special and idx != special)
            else:
                enabled = idx != self.container.current_layer
                checked = idx == self.container.current_layer

            btn.setEnabled(enabled)
            btn.setChecked(checked)

            # Set color
            color = "#1A9FFF" if idx == special else "white"
            btn.setStyleSheet(f"color: {color}")

        for widget in self.container.widgets:
            widget.setColor(QColor("#FFFFFF"))
            row = widget.desc.row
            col = widget.desc.col

            actuation = self.keyboard.actuation_matrix[self.profile][row][col]

            actuation_point = self.convert_to_nearest_10mm(actuation.actuation_point)
            rt_mode = actuation.rt_mode
            rt_press = self.convert_to_nearest_5mm(actuation.rt_press, self.switch_display_val)
            rt_release = self.convert_to_nearest_5mm(actuation.rt_release, self.switch_display_val)

            widget.setState(rt_mode)

            if index == 1:
                widget.setText(f"{actuation_point / 100:.1f}\n")
            elif index == 2:
                if rt_mode:
                    if rt_release != 0:
                        widget.setText(f"{rt_press / 100:.2f}\n{rt_release / 100:.2f}")
                    else:
                        widget.setText(f"{rt_press / 100:.2f}\n")
                else:
                    widget.setText("")
            elif index in (0, 3):
                text = self.text_for_widget(widget, self.container.current_layer)
                widget.setText(text)

                if index == 3:
                    for layer, key1, key2, *_ in self.container.input_priority_pairs:
                        if layer == self.container.current_layer:
                            if widget == key1:
                                widget.setText("⇷")
                            elif widget == key2:
                                widget.setText("⇸")
                            else:
                                continue
                            widget.setColor(QColor("#1A9FFF"))
        self.container.update()

    def reload_settings(self):
        self.container.tab_index = 0
        self.container.last_key = self.container.widgets[0]
        self.input_priority_resolution = 0
        self.container.input_priority_pairs = []
        self.ak_max = 8
        self.edit_pair = None

        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        layer_label = QLabel(tr("HallEffect", "Layer"))
        self.button_layout.addWidget(layer_label)

        self.layer_buttons = []
        
        for x in range(self.keyboard.layers):
            btn = SquareButton(str(x))
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setRelSize(1.667)
            btn.setCheckable(True)
            btn.clicked.connect(lambda state, idx=x: self.switch_layer(idx))
            self.button_layout.addWidget(btn)
            self.layer_buttons.append(btn)

        self.button_layout.addStretch()

        self.special_layer_cmb.blockSignals(True)
        self.special_layer_cmb.clear()
        self.special_layer_cmb.addItems(["None"])

        for x in range(self.keyboard.layers):
            self.special_layer_cmb.addItems([str(x)])
        
        self.special_layer_cmb.blockSignals(False)

        row = self.container.widgets[0].desc.row
        col = self.container.widgets[0].desc.col

        self.profile = 0
        self.total_travel = [320, 340, 350, 380, 390]

        self.total_travel_cmb.blockSignals(True)
        for distance in self.total_travel:
            self.total_travel_cmb.addItems([f"{distance / 100:.1f} mm"])
        self.total_travel_cmb.blockSignals(False)

        # Display values
        self.switch_display_val = self.keyboard.switch_option
        self.special_layer_display_val = self.keyboard.special_layer

        self.total_travel_val = self.total_travel[self.switch_display_val]

        actuation = self.keyboard.actuation_matrix[self.profile][row][col]
        
        self.actuation_display_val = self.convert_to_nearest_10mm(actuation.actuation_point)
        self.rt_mode_display_val = actuation.rt_mode
        self.rt_press_display_val = self.convert_to_nearest_5mm(actuation.rt_press, self.switch_display_val)
        self.rt_release_display_val = self.convert_to_nearest_5mm(actuation.rt_release, self.switch_display_val)
        self.rt_separate_val = 0 if (self.rt_release_display_val == 0) else 2

        for pair in self.keyboard.input_priority_pairs:
            key1 = None
            key2 = None
            for key in self.container.widgets:
                row = key.desc.row
                col = key.desc.col

                if pair[1] == row and pair[2] == col:
                    key1 = key
                elif pair[3] == row and pair[4] == col:
                    key2 = key

            self.container.input_priority_pairs.append((pair[0], key1, key2, pair[5]))

        # print(self.container.input_priority_pairs)
        # print(self.actuation_display_val, self.rt_press_display_val, self.rt_release_display_val)

        self.tab_widget.setCurrentIndex(0)
        self.on_tab_changed(0)
        self.switch_layer(0)

        self.refresh_layout_display()
        self.refresh_settings_display()
        self.refresh_pairs_view()

        # for key in self.container.widgets:
        #     print(f"x={key.x}, y={key.y}, w={key.w}, h={key.h}, "
        #         f"rotation={key.rotation_angle}, rotation_x={key.rotation_x}, rotation_y={key.rotation_y}")

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.container.set_keys(self.keyboard.keys, self.keyboard.encoders)
            self.reload_settings()

        self.container.setEnabled(self.valid())

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.firmware_updated)