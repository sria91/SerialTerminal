#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import *
from collections import OrderedDict
import sys
import yaml


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
        self.parent = parent
        self.serialport = None

        self.fl_autoscroll = None
        self.fl_hexinput = None
        self.fl_log = None
        self.logfile = None
        self.logfile_location = 'received.log'

        self.qglt = QGridLayout()

        self.qflt = QFormLayout()
        self.qglt.addLayout(self.qflt, 0, 0)

        self.qcb_ports = QComboBox()
        self.qcb_ports.setMinimumWidth(150)
        self.qcb_ports.currentTextChanged.connect(self.action_ports)
        self.qflt.addRow("Serial Port:", self.qcb_ports)

        self.qcb_baudrates = QComboBox()
        self.qcb_baudrates.addItems(list(self.baudrates))
        self.qcb_baudrates.currentTextChanged.connect(self.action_baud)
        self.qflt.addRow("Baud rate:", self.qcb_baudrates)

        self.qcb_databits = QComboBox()
        self.qcb_databits.addItems(list(self.databits))
        self.qcb_databits.currentTextChanged.connect(self.action_data)
        self.qcb_paritybit = QComboBox()
        self.qcb_paritybit.addItems(list(self.paritybit))
        self.qcb_paritybit.currentTextChanged.connect(self.action_parity)
        self.qcb_stopbits = QComboBox()
        self.qcb_stopbits.addItems(list(self.stopbits))
        self.qcb_stopbits.currentTextChanged.connect(self.action_stop)
        self.qcb_flowcontrol = QComboBox()
        self.qcb_flowcontrol.addItems(list(self.flowcontrol))
        self.qcb_flowcontrol.currentTextChanged.connect(self.action_flow)
        self.qbtn_refresh = QPushButton("Refresh")
        self.qbtn_refresh.clicked.connect(self.action_refresh)
        self.qbtn_connect_disconnect = QPushButton("Connect")
        self.qbtn_connect_disconnect.clicked.connect(self.action_connect)

        self.qflt.addRow("Data bits:", self.qcb_databits)
        self.qflt.addRow("Parity:", self.qcb_paritybit)
        self.qflt.addRow("Stop bits:", self.qcb_stopbits)
        self.qflt.addRow("Flow control:", self.qcb_flowcontrol)
        self.qflt.addWidget(self.qbtn_refresh)
        self.qflt.addWidget(self.qbtn_connect_disconnect)

        self.qtb_receiver = QTextBrowser()
        self.qtb_receiver.setWordWrapMode(QTextOption.NoWrap)
        self.qtb_receiver.setFont(fixedWidthFont)
        self.qtb_receiver.setMinimumWidth(400)
        self.qglt.addWidget(self.qtb_receiver, 0, 1)

        self.qhlt_receiver = QHBoxLayout()
        self.qchb_autoscroll_receiver = QCheckBox("Autoscroll")
        self.qchb_autoscroll_receiver.clicked.connect(self.action_autoscroll)
        self.qchb_autoscroll_receiver.click()
        self.qhlt_receiver.addWidget(self.qchb_autoscroll_receiver)
        self.qchb_receiver_log = QCheckBox("Log to")
        self.qchb_receiver_log.clicked.connect(self.action_log)
        self.qhlt_receiver.addWidget(self.qchb_receiver_log)
        self.qle_receiver_log = QLineEdit()
        self.qle_receiver_log.setPlaceholderText(self.logfile_location)
        self.qhlt_receiver.addWidget(self.qle_receiver_log)
        self.qbtn_receiver_log = QPushButton("...")
        self.qbtn_receiver_log.clicked.connect(self.action_receiver_log)
        self.qbtn_receiver_log.setFixedWidth(30)
        self.qhlt_receiver.addWidget(self.qbtn_receiver_log)
        self.qbtn_clear_receiver = QPushButton("Clear")
        self.qbtn_clear_receiver.clicked.connect(self.action_clear_receiver)
        self.qbtn_clear_receiver.setFixedWidth(70)
        self.qhlt_receiver.addWidget(self.qbtn_clear_receiver)
        self.qglt.addLayout(self.qhlt_receiver, 1, 1)

        self.qtb_sender = QTextBrowser()
        self.qtb_sender.setFont(fixedWidthFont)
        self.qtb_sender.setFixedHeight(100)
        self.qglt.addWidget(self.qtb_sender, 2, 1)

        self.qchb_hexinput = QCheckBox("Hex")
        self.qchb_hexinput.clicked.connect(self.action_hexinput)
        self.qle_sender = QLineEdit()
        self.qle_sender.returnPressed.connect(self.return_pressed)
        self.qcb_lineending = QComboBox()
        self.qcb_lineending.addItems(self.lineendings)
        self.qcb_lineending.currentTextChanged.connect(self.action_lineending)
        self.qbtn_sender = QPushButton("Send")
        self.qbtn_sender.clicked.connect(self.action_input)
        self.qhlt_sender = QHBoxLayout()
        self.qhlt_sender.addWidget(self.qchb_hexinput)
        self.qhlt_sender.addWidget(self.qle_sender)
        self.qhlt_sender.addWidget(self.qcb_lineending)
        self.qhlt_sender.addWidget(self.qbtn_sender)
        self.qglt.addLayout(self.qhlt_sender, 3,1)

        self.qhlt_session = QHBoxLayout()
        self.qbtn_save_session = QPushButton("Save session")
        self.qbtn_save_session.clicked.connect(self.action_save_session)
        self.qhlt_session.addWidget(self.qbtn_save_session)
        self.qbtn_load_session = QPushButton("Load session")
        self.qbtn_load_session.clicked.connect(self.action_load_session)
        self.qhlt_session.addWidget(self.qbtn_load_session)
        self.qglt.addLayout(self.qhlt_session, 3, 0)

        self.setLayout(self.qglt)

        self.serialport_name = None
        self.baud = '9600'
        self.data = '8'
        self.parity = 'None'
        self.stop = '1'
        self.flow = 'None'
        self.lineending = ''
        self.action_refresh()

    def action_ports(self, serial_portname):
        self.serialport_name = serial_portname

    def action_baud(self, baud):
        self.baud = baud

    def action_data(self, data):
        self.data = data

    def action_parity(self, parity):
        self.parity = parity

    def action_stop(self, stop):
        self.stop = stop

    def action_flow(self, flow):
        self.flow = flow

    def action_lineending(self, lineending):
        self.lineending = self.lineendings[lineending]

    def action_save_session(self):
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

    def action_load_session(self):
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
        self.action_refresh()
        if self.fl_log:
            self.qle_receiver_log.setText(self.logfile_location)

    def action_receiver_log(self):
        logfile_location = QFileDialog.getSaveFileName(self, 'Save file', '.', 'Log files (*.log)')[0]
        if logfile_location:
            self.logfile_location = logfile_location
            self.qle_receiver_log.setText(self.logfile_location)
            self.qchb_receiver_log.click()

    def action_log(self):
        self.fl_log = not self.fl_log
        if self.fl_log:
            self.logfile = open(self.logfile_location, 'w')

    def action_hexinput(self):
        self.fl_hexinput = not self.fl_hexinput

    def action_clear_receiver(self):
        self.qtb_receiver.clear()

    def action_refresh(self):
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

    def action_connect(self):
        self.serialport_name = self.qcb_ports.currentText()
        self.serialport = QSerialPort()
        self.serialport.setPortName(self.serialport_name)
        self.serialport.setBaudRate(self.baudrates[self.qcb_baudrates.currentText()])
        self.serialport.setDataBits(self.databits[self.qcb_databits.currentText()])
        self.serialport.setParity(self.paritybit[self.qcb_paritybit.currentText()])
        self.serialport.setStopBits(self.stopbits[self.qcb_stopbits.currentText()])
        self.serialport.setFlowControl(QSerialPort.NoFlowControl)
        # self.serialport.close()
        self.serialport.open(QIODevice.ReadWrite)
        if self.serialport.isOpen():
            self.serialport.readyRead.connect(self.ready_read)
            self.qbtn_connect_disconnect.setText("Disconnect")
            self.qbtn_connect_disconnect.disconnect()
            self.qbtn_connect_disconnect.clicked.connect(self.action_disconnect)
            if self.fl_log:
                self.logfile = open(self.logfile_location, 'w')

            self.qcb_ports.setDisabled(True)
            self.qcb_baudrates.setDisabled(True)
            self.qcb_databits.setDisabled(True)
            self.qcb_paritybit.setDisabled(True)
            self.qcb_stopbits.setDisabled(True)
            self.qcb_flowcontrol.setDisabled(True)
            self.qbtn_refresh.setDisabled(True)
            self.qbtn_load_session.setDisabled(True)

    def action_disconnect(self):
        self.serialport.close()
        self.qbtn_connect_disconnect.setText("Connect")
        self.qbtn_connect_disconnect.disconnect()
        self.qbtn_connect_disconnect.clicked.connect(self.action_connect)
        if self.fl_log:
            self.logfile.close()

        self.qcb_ports.setEnabled(True)
        self.qcb_baudrates.setEnabled(True)
        self.qcb_databits.setEnabled(True)
        self.qcb_paritybit.setEnabled(True)
        self.qcb_stopbits.setEnabled(True)
        self.qcb_flowcontrol.setEnabled(True)
        self.qbtn_refresh.setEnabled(True)
        self.qbtn_load_session.setEnabled(True)

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

    def action_autoscroll(self):
        self.fl_autoscroll = not self.fl_autoscroll

    def return_pressed(self):
        self.action_input()

    def action_input(self):
        if self.serialport:
            text_to_send = self.qle_sender.text()
            bytes_to_send = bytes(text_to_send + self.lineending, "utf-8")
            if self.fl_hexinput is True and text_to_send.find('\\x') == 0:
                self.serialport.writeData(bytes.fromhex(text_to_send[2:]))
            else:
                self.serialport.writeData(bytes_to_send)
            self.qtb_sender.append(text_to_send)

    def closeEvent(self, a0):
        if self.serialport:
            self.serialport.close()
        super(SerialTerminalWidget, self).close()


class SerialTerminal(QMainWindow):
    def __init__(self):
        super(SerialTerminal, self).__init__()
        self.setWindowTitle("Serial Terminal")

        serial_terminal_widget = SerialTerminalWidget(self)
        self.setCentralWidget(serial_terminal_widget)

        menubar = self.menuBar()
        menubar.setVisible(True)

        statusbar = self.statusBar()
        statusbar.setVisible(True)


app = QApplication(sys.argv)
fixedWidthFont = QFont('Consolas')
if not fixedWidthFont.exactMatch():
    fixedWidthFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
widget = SerialTerminal()
widget.show()
app.exec_()
