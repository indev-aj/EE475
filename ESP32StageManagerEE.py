from imswitch.imcommon.model import initLogger
from .PositionerManager import PositionerManager
import time
import numpy as np


class ESP32StageManagerEE(PositionerManager):

    def __init__(self, positionerInfo, name, **lowLevelManagers):
        super().__init__(positionerInfo, name, initialPosition={
            axis: 0 for axis in positionerInfo.axes
        })

        self._rs232manager = lowLevelManagers['rs232sManager'][
            positionerInfo.managerProperties['rs232device']
        ]

        self.__logger = initLogger(self, instanceName=name)
        self.board = self._rs232manager._esp32

    def move(self, value: float, axis: str):
        if axis == 'X':
            self.board.move_rel((value, 0, 0), blocking=False)
        elif axis == 'Y':
            self.board.move_rel((0, value, 0), blocking=False)
        elif axis == 'Z':
            self.board.move_rel((0, 0, value), blocking=False)
        else:
            self.__logger.warning('Wrong axis, has to be "X" "Y" or "Z"')
            return
        self._position[axis] = self._position[axis] + value

    def setPosition(self, value: float, axis: str):
        self._position[axis] = value

    # test arrow key input
    from PyQt5 import QtCore

    @shortcut(QtCore.Qt.Key_Up, "Move up")
    def key_moveXup(self):
        self.move(value=100, axis="X")

    @shortcut(QtCore.Qt.Key_Down, "Move down")
    def key_moveXdown(self):
        self.move(value=-100, axis="X")

    @shortcut(QtCore.Qt.Key_Left, "Move left")
    def key_moveYleft(self):
        self.move(value=-100, axis="Y")

    @shortcut(QtCore.Qt.Key_Right, "Move right")
    def key_moveYright(self):
        self.move(value=100, axis="Y")

    @shortcut("-", "Move Z up")
    def key_moveZup(self):
        self.move(value=100, axis="Z")

    @shortcut("+", "Move Z down")
    def key_moveZdown(self):
        self.move(value=-100, axis="Z")

# Copyright (C) 2020, 2021 The imswitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
