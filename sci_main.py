# -*- coding: utf-8 -*-
__author__ = 'wuliaodew'
__name__ = '__main__'

from PyQt4 import QtCore, QtGui
from matplotlib.figure import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import re

import sys, struct, sci_tool, serial, time, threading


#数据位
SERIAL_DATABIT_ARRAY = (serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS, serial.FIVEBITS)
#停止位
SERIAL_STOPBIT_ARRAY = (serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)
#校验位
SERIAL_CHECKBIT_ARRAY = (serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD , serial.PARITY_MARK, serial.PARITY_SPACE)


class SciWidgetClass( QtCore.QObject):
    SciReceive =  QtCore.pyqtSignal()

class Sci_UiCtl(sci_tool.Ui_MainWindow):
    def __init__(self,MainWindow):
        super(sci_tool.Ui_MainWindow, self).__init__()
        self.__index = 0
        self.setupUi(MainWindow)#display sci tool menu

        self.portstatus_flag = False
        self._serial = serial.Serial()#init serial class
        self.sciopenButton.connect(self.sciopenButton, QtCore.SIGNAL('clicked()'), self.SciOpenButton_Click)#connect button click func
        self.test = 0

        self.scirec_signal = SciWidgetClass()
        self.scirec_signal.SciReceive.connect(self.SciWinReFresh)
      #  self.scirec_signal.connect(self.scirec_signal, QtCore.SIGNAL('SCI RECEIVE'), self.SciWinReFresh())

        try:
            self.scithread = threading.Thread(target=self.SciReadData)
            self.scithread.setDaemon(True)
            self.scithread.start()
        except:
             QtGui.QMessageBox.warning(None, '错误警告',"SCI读取线程未创建", QtGui.QMessageBox.Ok)

    def SciOpenButton_Click(self):
         clickstatus = self.sciopenButton.isChecked()
         if clickstatus:
                #得到串口的设置参数
            comread = int(self.portcomtext.text())-1
            bandrate = int(self.baudratecombo.currentText())
            databit = SERIAL_DATABIT_ARRAY[self.databitcombo.currentIndex()]
            stopbit = SERIAL_STOPBIT_ARRAY[self.stopbitcombo.currentIndex()]
            checkbit = SERIAL_CHECKBIT_ARRAY[self.checkbitcombo.currentIndex()]

            #打开串口
            try:
                self._serial = serial.Serial(comread)
                self._serial.baudrate = bandrate
                self._serial.bytesize = databit
                self._serial.parity = checkbit
                self._serial.stopbits = stopbit
            except (OSError, serial.SerialException):
                QtGui.QMessageBox.warning(None, '端口警告',"端口无效或者不存在", QtGui.QMessageBox.Ok)

            if self._serial.isOpen():
                self.sciopenButton.setText("关闭")
                self.baudratecombo.setEnabled(False)
                self.checkbitcombo.setEnabled(False)
                self.databitcombo.setEnabled(False)
                self.stopbitcombo.setEnabled(False)
                self.portcomtext.setEnabled(False)
                self.portstatus_flag = True
            else:
                self.sciopenButton.setChecked(False)
         else:
            self._serial.close()
            self.sciopenButton.setText("打开")
            self.baudratecombo.setEnabled(True)
            self.stopbitcombo.setEnabled(True)
            self.databitcombo.setEnabled(True)
            self.checkbitcombo.setEnabled(True)
            self.portcomtext.setEnabled(True)
            self.portstatus_flag = False

    @QtCore.pyqtSlot()
    def SciWinReFresh(self):
        self.dishex.append('test')

###############################################
#数据接收线程
    def SciReadData(self):#deal sci data
        while True:
            if self.portstatus_flag == True:
                self.scirec_signal.SciReceive.emit()
                time.sleep(0.1)
            else:
                time.sleep(1)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Sci_UiCtl(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())