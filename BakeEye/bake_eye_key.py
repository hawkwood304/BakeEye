from maya.cmds import namespace
from shiboken2 import wrapInstance
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import os
import maya.cmds as cm
# import pymel.core as pm
import maya.OpenMaya as oM
import maya.OpenMayaUI as oMUI

from PySide2 import QtWidgets, QtCore, QtGui
from maya.mel import eval


# import sys


class QHLine(QtWidgets.QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class QVLine(QtWidgets.QFrame):

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class QHLineName(QtWidgets.QGridLayout):

    def __init__(self, name):
        super(QHLineName, self).__init__()
        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setStyleSheet("font: italic 9pt;" "color: azure;")
        self.addWidget(name_lb, 0, 0, 1, 1)
        self.addWidget(QHLine(), 0, 1, 1, 2)


# noinspection PyAttributeOutsideInit
class BakeEye(QtWidgets.QWidget):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    def __init__(self):
        super(BakeEye, self).__init__()

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.name_space_lb = QtWidgets.QLabel("Namespace:")
        self.name_space_le = QtWidgets.QLineEdit()
        self.name_space_assign_btn = QtWidgets.QPushButton("Assign")

        self.connect_arkit_to_control_btn = QtWidgets.QPushButton("Connect arkit to control and bake")

    def create_layouts(self):
        name_space_layout = QtWidgets.QHBoxLayout()
        name_space_layout.addWidget(self.name_space_lb)
        name_space_layout.addWidget(self.name_space_le)
        name_space_layout.addWidget(self.name_space_assign_btn)

        command_layout = QtWidgets.QHBoxLayout()
        command_layout.addWidget(self.connect_arkit_to_control_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(name_space_layout)
        main_layout.addLayout(command_layout)

    def create_connections(self):
        self.name_space_assign_btn.clicked.connect(self.get_char_namespace)
        self.connect_arkit_to_control_btn.clicked.connect(self.connect_arkit_to_control)

    def get_char_namespace(self):
        list_selected_object = cm.ls(sl=True)
        selected_object = ""
        if len(list_selected_object) != 1:
            oM.MGlobal_displayError("Please chose only one object to process")
        else:
            selected_object = list_selected_object[0]

        name_space = selected_object.rpartition(":")[0]
        self.name_space_le.setText(name_space)
        return name_space

    @staticmethod
    def execute_mel_command(command):
        try:
            eval(command)
            # logger.info(f"MEL command executed: {command}")
        except RuntimeError as e:
            logger.error(f"Failed to execute MEL command: {command} - {e}")

    def connect_arkit_to_control(self):
        name_space = self.get_char_namespace()
        apple_control_name = "ctrlARKitBS_M"
        eye_right_control_name = "ctrlEye_R"
        eye_left_control_name = "ctrlEye_L"
        node_clean_after = []
        if name_space:
            apple_control_name = f"{name_space}:{apple_control_name}"
            eye_right_control_name = f"{name_space}:{eye_right_control_name}"
            eye_left_control_name = f"{name_space}:{eye_left_control_name}"

        # eyeBlinkLeft
        cm.createNode("unitConversion", name=f"eyeBlinkLeft_uC")
        node_clean_after.append("eyeBlinkLeft_uC")
        cm.setAttr(f"eyeBlinkLeft_uC.conversionFactor", 1)
        cm.connectAttr(f"{apple_control_name}.eyeBlinkLeft", f"eyeBlinkLeft_uC.input", force=True)
        cm.connectAttr(f"eyeBlinkLeft_uC.output", f"{eye_left_control_name}.blink", force=True)

        # eyeBlinkRight
        cm.createNode("unitConversion", name=f"eyeBlinkRight_uC")
        node_clean_after.append("eyeBlinkRight_uC")
        cm.setAttr(f"eyeBlinkRight_uC.conversionFactor", 1)
        cm.connectAttr(f"{apple_control_name}.eyeBlinkRight", f"eyeBlinkRight_uC.input", force=True)
        cm.connectAttr(f"eyeBlinkRight_uC.output", f"{eye_right_control_name}.blink", force=True)

        # eyeSquintLeft
        cm.createNode("unitConversion", name=f"eyeSquintLeft_uC")
        node_clean_after.append("eyeSquintLeft_uC")
        cm.setAttr(f"eyeSquintLeft_uC.conversionFactor", 1)
        cm.connectAttr(f"{apple_control_name}.eyeSquintLeft", f"eyeSquintLeft_uC.input", force=True)
        cm.connectAttr(f"eyeSquintLeft_uC.output", f"{eye_left_control_name}.squint", force=True)

        # eyeSquintRight
        cm.createNode("unitConversion", name=f"eyeSquintRight_uC")
        node_clean_after.append("eyeSquintRight_uC")
        cm.setAttr(f"eyeSquintRight_uC.conversionFactor", 1)
        cm.connectAttr(f"{apple_control_name}.eyeSquintRight", f"eyeSquintRight_uC.input", force=True)
        cm.connectAttr(f"eyeSquintRight_uC.output", f"{eye_right_control_name}.squint", force=True)

        # eyeLookDownLeft and eyeLookUpLeft
        cm.createNode("unitConversion", name=f"eyeLookDownLeft_uC")
        node_clean_after.append("eyeLookDownLeft_uC")
        cm.setAttr(f"eyeLookDownLeft_uC.conversionFactor", -0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookDownLeft", f"eyeLookDownLeft_uC.input", force=True)

        cm.createNode("unitConversion", name=f"eyeLookUpLeft_uC")
        node_clean_after.append("eyeLookUpLeft_uC")
        cm.setAttr(f"eyeLookUpLeft_uC.conversionFactor", 0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookUpLeft", f"eyeLookUpLeft_uC.input", force=True)

        cm.createNode("plusMinusAverage", name="eyeLookDownLeft_eyeLookUpLeft_bW")
        node_clean_after.append("eyeLookDownLeft_eyeLookUpLeft_bW")
        cm.connectAttr(f"eyeLookDownLeft_uC.output", f"eyeLookDownLeft_eyeLookUpLeft_bW.input1D[0]", force=True)
        cm.connectAttr(f"eyeLookUpLeft_uC.output", f"eyeLookDownLeft_eyeLookUpLeft_bW.input1D[1]", force=True)
        cm.connectAttr(f"eyeLookDownLeft_eyeLookUpLeft_bW.output1D", f"{eye_left_control_name}.translateY", force=True)

        # eyeLookDownRight and eyeLookUpRight
        cm.createNode("unitConversion", name=f"eyeLookDownRight_uC")
        node_clean_after.append("eyeLookDownRight_uC")
        cm.setAttr(f"eyeLookDownRight_uC.conversionFactor", -0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookDownRight", f"eyeLookDownRight_uC.input", force=True)

        cm.createNode("unitConversion", name=f"eyeLookUpRight_uC")
        node_clean_after.append("eyeLookUpRight_uC")
        cm.setAttr(f"eyeLookUpRight_uC.conversionFactor", 0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookUpRight", f"eyeLookUpRight_uC.input", force=True)

        cm.createNode("plusMinusAverage", name="eyeLookDownRight_eyeLookUpRight_bW")
        node_clean_after.append("eyeLookDownRight_eyeLookUpRight_bW")
        cm.connectAttr(f"eyeLookDownRight_uC.output", f"eyeLookDownRight_eyeLookUpRight_bW.input1D[0]", force=True)
        cm.connectAttr(f"eyeLookUpRight_uC.output", f"eyeLookDownRight_eyeLookUpRight_bW.input1D[1]", force=True)
        cm.connectAttr(f"eyeLookDownRight_eyeLookUpRight_bW.output1D", f"{eye_right_control_name}.translateY",
                       force=True)

        # eyeLookInLeft and eyeLookOutLeft
        cm.createNode("unitConversion", name=f"eyeLookInLeft_uC")
        node_clean_after.append("eyeLookInLeft_uC")
        cm.setAttr(f"eyeLookInLeft_uC.conversionFactor", -0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookInLeft", f"eyeLookInLeft_uC.input", force=True)

        cm.createNode("unitConversion", name=f"eyeLookOutLeft_uC")
        node_clean_after.append("eyeLookOutLeft_uC")
        cm.setAttr(f"eyeLookOutLeft_uC.conversionFactor", 0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookOutLeft", f"eyeLookOutLeft_uC.input", force=True)

        cm.createNode("plusMinusAverage", name="eyeLookInLeft_eyeLookOutLeft_bW")
        node_clean_after.append("eyeLookInLeft_eyeLookOutLeft_bW")
        cm.connectAttr(f"eyeLookInLeft_uC.output", f"eyeLookInLeft_eyeLookOutLeft_bW.input1D[0]", force=True)
        cm.connectAttr(f"eyeLookOutLeft_uC.output", f"eyeLookInLeft_eyeLookOutLeft_bW.input1D[1]", force=True)
        cm.connectAttr(f"eyeLookInLeft_eyeLookOutLeft_bW.output1D", f"{eye_left_control_name}.translateX", force=True)

        # eyeLookInRight and eyeLookOutRight
        cm.createNode("unitConversion", name=f"eyeLookInRight_uC")
        node_clean_after.append("eyeLookInRight_uC")
        cm.setAttr(f"eyeLookInRight_uC.conversionFactor", 0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookInRight", f"eyeLookInRight_uC.input", force=True)

        cm.createNode("unitConversion", name=f"eyeLookOutRight_uC")
        node_clean_after.append("eyeLookOutRight_uC")
        cm.setAttr(f"eyeLookOutRight_uC.conversionFactor", -0.1)
        cm.connectAttr(f"{apple_control_name}.eyeLookOutRight", f"eyeLookOutRight_uC.input", force=True)

        cm.createNode("plusMinusAverage", name="eyeLookInRight_eyeLookOutRight_bW")
        node_clean_after.append("eyeLookInRight_eyeLookOutRight_bW")
        cm.connectAttr(f"eyeLookInRight_uC.output", f"eyeLookInRight_eyeLookOutRight_bW.input1D[0]", force=True)
        cm.connectAttr(f"eyeLookOutRight_uC.output", f"eyeLookInRight_eyeLookOutRight_bW.input1D[1]", force=True)
        cm.connectAttr(f"eyeLookInRight_eyeLookOutRight_bW.output1D", f"{eye_right_control_name}.translateX",
                       force=True)

        cm.select(eye_right_control_name, eye_left_control_name)
        min_time = int(cm.playbackOptions(q=True, min=True))
        max_time = int(cm.playbackOptions(q=True, max=True))

        self.execute_mel_command(
            f'bakeResults -simulation true -t "{min_time}:{max_time}" -sampleBy 1 -oversamplingRate 1 '
            f'-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
            f'-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false '
            f'-minimizeRotation true -controlPoints false -shape true;'
        )
        try:
            cm.delete(node_clean_after)
        except ValueError:
            pass
        attribute_name = ['eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft',
                          'eyeSquintLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight',
                          'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight']
        for i in attribute_name:
            cm.cutKey(apple_control_name, clear=True, attribute=i)
            cm.setAttr(f"{apple_control_name}.{i}", 0)


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyMethodOverriding
class MainWindow(QtWidgets.QDialog):
    WINDOW_TITLE = "Bake Eye To Control"

    SCRIPTS_DIR = cm.internalVar(userScriptDir=True)
    ICON_DIR = os.path.join(SCRIPTS_DIR, 'Thi/Icon')

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = MainWindow()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()

        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """

        Returns: The Maya main window widget as a Python object

        """
        main_window_ptr = oMUI.MQtUtil.mainWindow()
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(MainWindow, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.geometry = None

        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 100)
        self.create_widget()
        self.create_layouts()
        self.create_connections()

    def create_widget(self):
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.addWidget(BakeEye())

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layouts(self):

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.content_layout)

    def create_connections(self):
        self.close_btn.clicked.connect(self.close)

    def showEvent(self, e):
        super(MainWindow, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        super(MainWindow, self).closeEvent(e)

        self.geometry = self.saveGeometry()
