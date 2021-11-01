# -*- coding: utf-8 -*-
"""
Collection of modular GUIs that can be used for creating SLM patterns.

When a new SLM class is called, the GUI created adds any of the following to a pyqtgraph.DockArea by importing them by
name (so the naming of these classes is not arbitrary).
"""
from __future__ import division

import os
from builtins import str

import numpy as np
from past.utils import old_div

from nplab.ui.ui_tools import UiTools
from nplab.utils.gui import QtWidgets, uic


class BaseUi(QtWidgets.QWidget, UiTools):
    def __init__(self, slm_gui, name):
        super(BaseUi, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui_%s.ui' % name), self)
        self.slm_gui = slm_gui
        self._connect()

    def _connect(self):
        return

    def get_params(self):
        """
        :return: list of parameters to be passed to the pattern_generator of the same name as the class
        """
        raise NotImplementedError


class constantUi(BaseUi):
    def __init__(self, slm_gui):
        super(constantUi, self).__init__(slm_gui, 'constant')

    def _connect(self):
        self.offset_slider.valueChanged.connect(self.update_offset_lineedit)
        self.offset_lineEdit.returnPressed.connect(self.update_offset_slider)
        self.offset_slider.valueChanged.connect(self.slm_gui.make)

    def update_offset_lineedit(self):
        steps = self.offset_slider.value()
        value = 2 * steps / 100.
        self.offset_lineEdit.setText('%g' % value)

    def update_offset_slider(self):
        value = float(self.offset_lineEdit.text())
        steps = 100 * value / 2.
        self.offset_slider.setValue(steps)

    def get_params(self):
        return np.pi * float(self.offset_lineEdit.text()),


class calibration_responsivenessUi(BaseUi):
    def __init__(self, slm_gui):
        super(calibration_responsivenessUi, self).__init__(slm_gui, 'calibration_responsiveness')

    def _connect(self):
        self.offset_slider.valueChanged.connect(self.update_offset_lineedit)
        self.offset_lineEdit.returnPressed.connect(self.update_offset_slider)

    def update_offset_lineedit(self):
        steps = self.offset_slider.value()
        value = 2 * steps / 100.
        self.offset_lineEdit.setText('%g' % value)

    def update_offset_slider(self):
        value = float(self.offset_lineEdit.text())
        steps = 100 * value / 2.
        self.offset_slider.setValue(steps)

    def get_params(self):
        return np.pi * float(self.offset_lineEdit.text()), int(self.spinBox_axis.value())


class gratingsUi(BaseUi):
    def __init__(self, slm_gui):
        super(gratingsUi, self).__init__(slm_gui, 'gratings')

    def _connect(self):
        self.pushButton_center.clicked.connect(lambda: self.update_gratings('center'))
        self.pushButton_up.clicked.connect(lambda: self.update_gratings('up'))
        self.pushButton_down.clicked.connect(lambda: self.update_gratings('down'))
        self.pushButton_left.clicked.connect(lambda: self.update_gratings('left'))
        self.pushButton_right.clicked.connect(lambda: self.update_gratings('right'))
        self.gratingx_lineEdit.textChanged.connect(self.slm_gui.make)
        self.gratingy_lineEdit.textChanged.connect(self.slm_gui.make)

    def update_gratings(self, direction):
        step = float(self.lineEdit_step.text())
        grating_x = float(self.gratingx_lineEdit.text())
        grating_y = float(self.gratingy_lineEdit.text())
        if direction == 'center':
            self.gratingx_lineEdit.setText(str(0))
            self.gratingy_lineEdit.setText(str(0))
        elif direction == 'up':
            self.gratingy_lineEdit.setText('%g' % (grating_y + step))
        elif direction == 'down':
            self.gratingy_lineEdit.setText('%g' % (grating_y - step))
        elif direction == 'left':
            self.gratingx_lineEdit.setText('%g' % (grating_x + step))
        elif direction == 'right':
            self.gratingx_lineEdit.setText('%g' % (grating_x - step))

    def get_params(self):
        grating_x = self.gratingx_lineEdit.text()
        grating_y = self.gratingy_lineEdit.text()
        if grating_x == '':
            grating_x = 0
        if grating_y == '':
            grating_y = 0
        return float(grating_x), float(grating_y)


class astigmatismUi(BaseUi):
    def __init__(self, slm_gui):
        super(astigmatismUi, self).__init__(slm_gui, 'astigmatism')

    def _connect(self):
        self.amplitude_step_lineEdit.returnPressed.connect(self.update_amplitude_lineedit)
        self.amplitude_offset_lineEdit.returnPressed.connect(self.update_amplitude_lineedit)
        self.amplitude_slider.valueChanged.connect(self.update_amplitude_lineedit)
        self.amplitude_lineEdit.returnPressed.connect(self.update_amplitude_slider)
        self.amplitude_slider.valueChanged.connect(self.slm_gui.make)

        self.angle_step_lineEdit.returnPressed.connect(self.update_angle_lineedit)
        self.angle_offset_lineEdit.returnPressed.connect(self.update_angle_lineedit)
        self.angle_slider.valueChanged.connect(self.update_angle_lineedit)
        self.angle_lineEdit.returnPressed.connect(self.update_angle_slider)
        self.angle_slider.valueChanged.connect(self.slm_gui.make)

    def update_amplitude_lineedit(self):
        try:
            step_size = float(self.amplitude_step_lineEdit.text())
        except ValueError:
            amplitude = float(self.amplitude_lineEdit.text())
            if amplitude != 0:
                step_size = 0.01 * amplitude
            else:
                step_size = 0.0001
            self.amplitude_step_lineEdit.setText(str(step_size))
        try:
            offset = float(self.amplitude_offset_lineEdit.text())
        except ValueError:
            offset = float(self.amplitude_lineEdit.text())
            self.amplitude_offset_lineEdit.setText(str(offset))
        steps = self.amplitude_slider.value()
        value = offset + steps * step_size

        self.amplitude_lineEdit.setText('%g' % value)

    def update_amplitude_slider(self):
        value = float(self.amplitude_lineEdit.text())
        step_size = float(self.amplitude_step_lineEdit.text())
        offset = float(self.amplitude_offset_lineEdit.text())

        steps = int(old_div((value - offset), step_size))
        self.amplitude_slider.setValue(steps)

    def update_angle_lineedit(self):
        try:
            step_size = float(self.angle_step_lineEdit.text())
        except ValueError:
            step_size = 1
            self.angle_step_lineEdit.setText(str(step_size))
        try:
            offset = float(self.angle_offset_lineEdit.text())
        except ValueError:
            offset = float(self.angle_lineEdit.text())
            self.angle_offset_lineEdit.setText(str(offset))
        steps = self.angle_slider.value()
        value = offset + steps * step_size

        self.angle_lineEdit.setText('%g' % value)

    def update_angle_slider(self):
        value = float(self.angle_lineEdit.text())
        step_size = float(self.angle_step_lineEdit.text())
        offset = float(self.angle_offset_lineEdit.text())

        steps = int(old_div((value - offset), step_size))
        self.angle_slider.setValue(steps)

    def get_params(self):
        amplitude = float(self.amplitude_lineEdit.text())
        angle = float(self.angle_lineEdit.text())
        return amplitude, angle


class focusUi(BaseUi):
    def __init__(self, slm_gui):
        super(focusUi, self).__init__(slm_gui, 'focus')

    def _connect(self):
        # Connects the offset slider to the lineEdits
        self.lineEdit_step.returnPressed.connect(self.update_lineedit)
        self.lineEdit_offset.returnPressed.connect(self.update_lineedit)
        self.slider.valueChanged.connect(self.update_lineedit)
        self.lineEdit_value.returnPressed.connect(self.update_slider)
        self.slider.valueChanged.connect(self.slm_gui.make)

    def update_lineedit(self):
        step_size = float(self.lineEdit_step.text())
        offset = float(self.lineEdit_offset.text())
        steps = self.slider.value()
        value = offset + steps * step_size

        self.lineEdit_value.setText('%g' % value)

    def update_slider(self):
        value = float(self.lineEdit_value.text())
        step_size = float(self.lineEdit_step.text())
        offset = float(self.lineEdit_offset.text())

        steps = int(old_div((value - offset), step_size))
        self.slider.setValue(steps)

    def get_params(self):
        curvature = float(self.lineEdit_value.text())
        return curvature,


class vortexbeamUi(BaseUi):
    def __init__(self, slm_gui):
        super(vortexbeamUi, self).__init__(slm_gui, 'vortexbeam')

    def _connect(self):
        self.pushButton_flip.clicked.connect(self.flip)

        self.slider_angle.valueChanged.connect(lambda: self.lineEdit_angle.setText('%g' % self.slider_angle.value()))
        self.lineEdit_angle.textChanged.connect(lambda: self.slider_angle.setValue(int(float(self.lineEdit_angle.text()))))

        self.slider_center_x.valueChanged.connect(lambda: self.lineEdit_center_x.setText('%g' % (self.slider_center_x.value()/100)))
        self.slider_center_y.valueChanged.connect(lambda: self.lineEdit_center_y.setText('%g' % (self.slider_center_y.value()/100)))
        self.lineEdit_center_x.textChanged.connect(lambda: self.slider_center_x.setValue(int(100*float(self.lineEdit_center_x.text()))))
        self.lineEdit_center_y.textChanged.connect(lambda: self.slider_center_y.setValue(int(100*float(self.lineEdit_center_y.text()))))

        self.lineEdit_order.textChanged.connect(self.slm_gui.make)
        self.lineEdit_angle.textChanged.connect(self.slm_gui.make)
        self.lineEdit_center_x.textChanged.connect(self.slm_gui.make)
        self.lineEdit_center_y.textChanged.connect(self.slm_gui.make)

    def flip(self):
        order = int(float(self.lineEdit_order.text()))
        self.lineEdit_order.setText(str(-order))

    def get_params(self):
        order = int(float(self.lineEdit_order.text()))
        angle = float(self.lineEdit_angle.text())
        center_x = float(self.lineEdit_center_x.text())
        center_y = float(self.lineEdit_center_y.text())
        return order, angle, (center_x, center_y)


class multispot_gratingUi(BaseUi):
    def __init__(self, slm_gui):
        super(multispot_gratingUi, self).__init__(slm_gui, 'multispot_grating')

    def _connect(self):
        self.slider_grating.valueChanged.connect(lambda: self.lineEdit_grating.setText('%g' % (self.slider_grating.value()/100)))
        self.lineEdit_grating.textChanged.connect(lambda: self.slider_grating.setValue(int(100*float(self.lineEdit_grating.text()))))

        self.lineEdit_grating.textChanged.connect(self.slm_gui.make)
        self.lineEdit_spots.textChanged.connect(self.slm_gui.make)

    def get_params(self):
        spots = int(float(self.lineEdit_spots.text()))
        grating = float(self.lineEdit_grating.text())
        return grating, spots


class linear_lutUi(BaseUi):
    def __init__(self, slm_gui):
        super(linear_lutUi, self).__init__(slm_gui, 'linear_lut')

    def _connect(self):
        # Connects the offset slider to the lineEdits
        self.offset_lineEdit_step.returnPressed.connect(self.update_offset_lineedit)
        self.offset_lineEdit_offset.returnPressed.connect(self.update_offset_lineedit)
        self.offset_slider.valueChanged.connect(self.update_offset_lineedit)
        self.offset_lineEdit.returnPressed.connect(self.update_offset_slider)
        self.offset_slider.valueChanged.connect(self.slm_gui.make)

        # Connects the contrast slider to the lineEdits
        self.contrast_lineEdit_step.returnPressed.connect(self.update_contrast_lineedit)
        self.contrast_lineEdit_offset.returnPressed.connect(self.update_contrast_lineedit)
        self.contrast_slider.valueChanged.connect(self.update_contrast_lineedit)
        self.contrast_lineEdit.returnPressed.connect(self.update_contrast_slider)
        self.contrast_slider.valueChanged.connect(self.slm_gui.make)

    def update_offset_lineedit(self):
        step_size = float(self.offset_lineEdit_step.text())
        offset = float(self.offset_lineEdit_offset.text())
        steps = self.offset_slider.value()
        value = offset + steps * step_size

        self.offset_lineEdit.setText('%g' % value)

    def update_offset_slider(self):
        value = float(self.offset_lineEdit.text())
        step_size = float(self.offset_lineEdit_step.text())
        offset = float(self.offset_lineEdit_offset.text())

        steps = int(old_div((value - offset), step_size))
        self.offset_slider.setValue(steps)

    def update_contrast_lineedit(self):
        step_size = float(self.contrast_lineEdit_step.text())
        offset = float(self.contrast_lineEdit_offset.text())
        steps = self.contrast_slider.value()
        value = offset + steps * step_size

        self.contrast_lineEdit.setText('%g' % value)

    def update_contrast_slider(self):
        value = float(self.contrast_lineEdit.text())
        step_size = float(self.contrast_lineEdit_step.text())
        offset = float(self.contrast_lineEdit_offset.text())

        steps = int(old_div((value - offset), step_size))
        self.contrast_slider.setValue(steps)

    def get_params(self):
        contrast = float(self.contrast_lineEdit.text())
        offset = float(self.offset_lineEdit.text())
        return contrast, offset
