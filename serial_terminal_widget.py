# -*- coding: utf-8 -*-
"""Serial Terminal Widget"""

__author__ = "Srikanth Anantharam"
__copyright__ = "Copyright 2017-NOW, Srikanth Anantharam"
__license__ = 'Apache License'
__email__ = "sria91@gmail.com"

import yaml
from collections import OrderedDict

from PyQt5.QtCore import QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QFontDatabase, QTextOption, QTextCursor
from PyQt5.QtWidgets import (QWidget, QGridLayout, QFormLayout, QHBoxLayout,
                             QComboBox, QCheckBox, QPushButton, QTextBrowser, 
                             QLineEdit, QFileDialog)


class SerialTerminalWidget(QWidget):
    baudrates = OrderedDict([
        ('1200', QSerialPort.Baud1200),
        ('2400', QSerialPort.Baud2400),
        ('4800', QSerialPort.Baud4800),
        ('9600', QSerialPort.Baud9600),
        ('19200', QSerialPort.Baud19200),
        ('38400', QSerialPort.Baud38400),
        ('57600', QSerialPort.Baud57600),
        ('115200', QSerialPort.Baud115200)
    ])
    databits = OrderedDict([
        ('5', QSerialPort.Data5),
        ('6', QSerialPort.Data6),
        ('7', QSerialPort.Data7),
        ('8', QSerialPort.Data8)
    ])
    paritybit = OrderedDict([
        ('None', QSerialPort.NoParity),
        ('Even', QSerialPort.EvenParity),
        ('Odd', QSerialPort.OddParity),
        ('Mark', QSerialPort.MarkParity),
        ('Space', QSerialPort.SpaceParity)
    ])
    stopbits = OrderedDict([
        ('1', QSerialPort.OneStop),
        ('1.5', QSerialPort.OneAndHalfStop),
        ('2', QSerialPort.TwoStop)
    ])
    flowcontrol = OrderedDict([
        ('None', QSerialPort.NoFlowControl),
        ('Hardware', QSerialPort.FlowControl),
    ])
    lineendings = OrderedDict([
        ('None', ''),
        ('LF', '\n'),
        ('CR', '\r'),
        ('CR/LF', '\r\n')
    ])

    def __init__(self, parent=None):
        super(SerialTerminalWidget, self).__init__(parent)

        fixed_width_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)

        self.setLayout(QGridLayout())

        self.serialport = None

        self.fl_autoscroll = None
        self.fl_hexinput = None
        self.fl_log = None
        self.logfile = None
        self.logfile_location = 'received.log'

        self.qfl = QFormLayout()
        self.layout().addLayout(self.qfl, 0, 0)

        self.qcb_ports = QComboBox()
        self.qcb_ports.setMinimumWidth(150)
        self.qcb_ports.currentTextChanged.connect(self.slot_ports)
        self.qfl.addRow("Serial Port:", self.qcb_ports)

        self.qcb_baudrates = QComboBox()
        self.qcb_baudrates.addItems(list(self.baudrates))
        self.qcb_baudrates.currentTextChanged.connect(self.slot_baud)
        self.qfl.addRow("Baud rate:", self.qcb_baudrates)

        self.qcb_databits = QComboBox()
        self.qcb_databits.addItems(list(self.databits))
        self.qcb_databits.currentTextChanged.connect(self.slot_data)
        self.qcb_paritybit = QComboBox()
        self.qcb_paritybit.addItems(list(self.paritybit))
        self.qcb_paritybit.currentTextChanged.connect(self.slot_parity)
        self.qcb_stopbits = QComboBox()
        self.qcb_stopbits.addItems(list(self.stopbits))
        self.qcb_stopbits.currentTextChanged.connect(self.slot_stop)
        self.qcb_flowcontrol = QComboBox()
        self.qcb_flowcontrol.addItems(list(self.flowcontrol))
        self.qcb_flowcontrol.currentTextChanged.connect(self.slot_flow)
        self.qpb_refresh = QPushButton("Refresh")
        self.qpb_refresh.clicked.connect(self.slot_refresh)
        self.qpb_connect_disconnect = QPushButton("Connect")
        self.qpb_connect_disconnect.clicked.connect(self.slot_connect)

        self.qfl.addRow("Data bits:", self.qcb_databits)
        self.qfl.addRow("Parity:", self.qcb_paritybit)
        self.qfl.addRow("Stop bits:", self.qcb_stopbits)
        self.qfl.addRow("Flow control:", self.qcb_flowcontrol)
        self.qfl.addWidget(self.qpb_refresh)
        self.qfl.addWidget(self.qpb_connect_disconnect)

        self.qtb_receiver = QTextBrowser()
        self.qtb_receiver.setWordWrapMode(QTextOption.NoWrap)
        self.qtb_receiver.setFont(fixed_width_font)
        self.qtb_receiver.setMinimumWidth(400)
        self.layout().addWidget(self.qtb_receiver, 0, 1)

        self.qhbl_receiver = QHBoxLayout()
        self.qchb_autoscroll_receiver = QCheckBox("Autoscroll")
        self.qchb_autoscroll_receiver.clicked.connect(self.slot_autoscroll)
        self.qchb_autoscroll_receiver.click()
        self.qhbl_receiver.addWidget(self.qchb_autoscroll_receiver)
        self.qchb_receiver_log = QCheckBox("Log to")
        self.qchb_receiver_log.clicked.connect(self.slot_log)
        self.qhbl_receiver.addWidget(self.qchb_receiver_log)
        self.qle_receiver_log = QLineEdit()
        self.qle_receiver_log.setPlaceholderText(self.logfile_location)
        self.qhbl_receiver.addWidget(self.qle_receiver_log)
        self.qpb_receiver_log = QPushButton("...")
        self.qpb_receiver_log.clicked.connect(self.slot_receiver_log)
        self.qpb_receiver_log.setFixedWidth(30)
        self.qhbl_receiver.addWidget(self.qpb_receiver_log)
        self.qpb_clear_receiver = QPushButton("Clear")
        self.qpb_clear_receiver.clicked.connect(self.slot_clear_receiver)
        self.qpb_clear_receiver.setFixedWidth(70)
        self.qhbl_receiver.addWidget(self.qpb_clear_receiver)
        self.layout().addLayout(self.qhbl_receiver, 1, 1)

        self.qtb_sender = QTextBrowser()
        self.qtb_sender.setFont(fixed_width_font)
        self.qtb_sender.setFixedHeight(100)
        self.layout().addWidget(self.qtb_sender, 2, 1)

        self.qchb_hexinput = QCheckBox("Hex")
        self.qchb_hexinput.clicked.connect(self.slot_hexinput)
        self.qle_sender = QLineEdit()
        self.qle_sender.returnPressed.connect(self.return_pressed)
        self.qcb_lineending = QComboBox()
        self.qcb_lineending.addItems(self.lineendings)
        self.qcb_lineending.currentTextChanged.connect(self.slot_lineending)
        self.qpb_sender = QPushButton("Send")
        self.qpb_sender.clicked.connect(self.slot_input)
        self.qhbl_sender = QHBoxLayout()
        self.qhbl_sender.addWidget(self.qchb_hexinput)
        self.qhbl_sender.addWidget(self.qle_sender)
        self.qhbl_sender.addWidget(self.qcb_lineending)
        self.qhbl_sender.addWidget(self.qpb_sender)
        self.layout().addLayout(self.qhbl_sender, 3, 1)

        self.qhbl_session = QHBoxLayout()
        self.qpb_save_session = QPushButton("Save session")
        self.qpb_save_session.clicked.connect(self.slot_save_session)
        self.qhbl_session.addWidget(self.qpb_save_session)
        self.qpb_load_session = QPushButton("Load session")
        self.qpb_load_session.clicked.connect(self.slot_load_session)
        self.qhbl_session.addWidget(self.qpb_load_session)
        self.layout().addLayout(self.qhbl_session, 3, 0)

        self.serialport_name = None
        self.baud = '9600'
        self.data = '8'
        self.parity = 'None'
        self.stop = '1'
        self.flow = 'None'
        self.lineending = ''
        self.slot_refresh()

    def slot_ports(self, serial_portname):
        self.serialport_name = serial_portname

    def slot_baud(self, baud):
        self.baud = baud

    def slot_data(self, data):
        self.data = data

    def slot_parity(self, parity):
        self.parity = parity

    def slot_stop(self, stop):
        self.stop = stop

    def slot_flow(self, flow):
        self.flow = flow

    def slot_lineending(self, lineending):
        self.lineending = self.lineendings[lineending]

    def slot_save_session(self):
        d = OrderedDict([
            ('baud', self.baud),
            ('data', self.data),
            ('parity', self.parity),
            ('stop', self.stop),
            ('flow', self.flow),
            ('fl_autoscroll', self.fl_autoscroll),
            ('fl_hexinput', self.fl_hexinput),
            ('fl_log', self.fl_log),
            ('logfile_location', self.logfile_location)
        ])
        with open('session.yaml', 'w') as f:
            yaml.dump(d, f)

    def slot_load_session(self):
        with open('session.yaml', 'r') as f:
            d = yaml.load(f)
            self.baud = d['baud']
            self.data = d['data']
            self.parity = d['parity']
            self.stop = d['stop']
            self.flow = d['flow']
            self.fl_autoscroll = d['fl_autoscroll']
            self.fl_hexinput = d['fl_hexinput']
            self.fl_log = d['fl_log']
            self.logfile_location = d['logfile_location']
        self.qchb_autoscroll_receiver.setChecked(self.fl_autoscroll is True)
        self.qchb_hexinput.setChecked(self.fl_hexinput is True)
        self.qchb_receiver_log.setChecked(self.fl_log is True)
        self.slot_refresh()
        if self.fl_log:
            self.qle_receiver_log.setText(self.logfile_location)

    def slot_receiver_log(self):
        logfile_location = QFileDialog.getSaveFileName(self, 'Save file', '.', 'Log files (*.log)')[0]
        if logfile_location:
            self.logfile_location = logfile_location
            self.qle_receiver_log.setText(self.logfile_location)
            self.qchb_receiver_log.click()

    def slot_log(self):
        self.fl_log = not self.fl_log
        if self.fl_log:
            self.logfile = open(self.logfile_location, 'w')

    def slot_hexinput(self):
        self.fl_hexinput = not self.fl_hexinput

    def slot_clear_receiver(self):
        self.qtb_receiver.clear()

    def slot_refresh(self):
        self.qcb_ports.clear()

        available_ports = QSerialPortInfo.availablePorts()
        serialports = [serialport.systemLocation() for serialport in available_ports]

        self.qcb_ports.addItems(serialports)
        self.qcb_ports.setCurrentText(self.serialport_name)
        self.qcb_baudrates.setCurrentText(self.baud)
        self.qcb_databits.setCurrentText(self.data)
        self.qcb_paritybit.setCurrentText(self.parity)
        self.qcb_stopbits.setCurrentText(self.stop)
        self.qcb_flowcontrol.setCurrentText(self.flow)

    def slot_connect(self):
        self.serialport_name = self.qcb_ports.currentText()
        self.serialport = QSerialPort()
        self.serialport.setPortName(self.serialport_name)
        self.serialport.setBaudRate(
            self.baudrates[self.qcb_baudrates.currentText()]
        )
        self.serialport.setDataBits(
            self.databits[self.qcb_databits.currentText()]
        )
        self.serialport.setParity(
            self.paritybit[self.qcb_paritybit.currentText()]
        )
        self.serialport.setStopBits(
            self.stopbits[self.qcb_stopbits.currentText()]
        )
        self.serialport.setFlowControl(QSerialPort.NoFlowControl)
        # self.serialport.close()
        self.serialport.open(QIODevice.ReadWrite)
        if self.serialport.isOpen():
            self.serialport.readyRead.connect(self.ready_read)
            self.qpb_connect_disconnect.setText("Disconnect")
            self.qpb_connect_disconnect.disconnect()
            self.qpb_connect_disconnect.clicked.connect(self.slot_disconnect)
            if self.fl_log:
                self.logfile = open(self.logfile_location, 'w')

            self.qcb_ports.setDisabled(True)
            self.qcb_baudrates.setDisabled(True)
            self.qcb_databits.setDisabled(True)
            self.qcb_paritybit.setDisabled(True)
            self.qcb_stopbits.setDisabled(True)
            self.qcb_flowcontrol.setDisabled(True)
            self.qpb_refresh.setDisabled(True)
            self.qpb_load_session.setDisabled(True)

    def slot_disconnect(self):
        self.serialport.close()
        self.qpb_connect_disconnect.setText("Connect")
        self.qpb_connect_disconnect.disconnect()
        self.qpb_connect_disconnect.clicked.connect(self.slot_connect)
        if self.fl_log:
            self.logfile.close()

        self.qcb_ports.setEnabled(True)
        self.qcb_baudrates.setEnabled(True)
        self.qcb_databits.setEnabled(True)
        self.qcb_paritybit.setEnabled(True)
        self.qcb_stopbits.setEnabled(True)
        self.qcb_flowcontrol.setEnabled(True)
        self.qpb_refresh.setEnabled(True)
        self.qpb_load_session.setEnabled(True)

    def ready_read(self):
        b = bytes(self.serialport.readAll())
        try:
            read_all = b.decode("utf-8")
        except UnicodeDecodeError:
            read_all = str(b)[2:-1]
        if self.fl_log and self.logfile:
                self.logfile.write(read_all)
        flag = self.fl_autoscroll
        if not flag:
            v_val = self.qtb_receiver.verticalScrollBar().value()
            h_val = self.qtb_receiver.horizontalScrollBar().value()
        self.qtb_receiver.moveCursor(QTextCursor.End)
        self.qtb_receiver.insertPlainText(read_all)
        if not flag:
            self.qtb_receiver.verticalScrollBar().setValue(v_val)
            self.qtb_receiver.horizontalScrollBar().setValue(h_val)

    def slot_autoscroll(self):
        self.fl_autoscroll = not self.fl_autoscroll

    def return_pressed(self):
        self.slot_input()

    def slot_input(self):
        if self.serialport:
            text_to_send = self.qle_sender.text()
            bytes_to_send = bytes(text_to_send + self.lineending, "utf-8")
            if self.fl_hexinput is True and text_to_send.find('\\x') == 0:
                self.serialport.writeData(bytes.fromhex(text_to_send[2:]))
            else:
                self.serialport.writeData(bytes_to_send)
            self.qtb_sender.append(text_to_send)
