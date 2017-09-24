# -*- coding: utf-8 -*-
"""Serial Terminal"""

__author__ = "Srikanth Anantharam"
__copyright__ = "Copyright 2017-NOW, Srikanth Anantharam"
__license__ = 'Apache License'
__email__ = "sria91@gmail.com"

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QAction

from serial_terminal_widget import SerialTerminalWidget


class SerialTerminal(QMainWindow):
    """The SerialTerminal class."""

    def __init__(self, parent=None):
        super(SerialTerminal, self).__init__(parent)
        self.setWindowTitle("Serial Terminal")

        self.setCentralWidget(SerialTerminalWidget())

        menubar = self.menuBar()
        self.menu_file = menubar.addMenu("File")
        self.action_close = QAction("Close")
        self.action_close.setShortcut("Ctrl+Q")
        self.action_close.triggered.connect(self.close)
        self.menu_file.addAction(self.action_close)
        menubar.setVisible(True)

        statusbar = self.statusBar()
        statusbar.setVisible(True)


def main():
    """The main function."""
    app = QApplication(sys.argv)
    widget = SerialTerminal()
    widget.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
