#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aleksameter Reflectance Calculation Tool
Main Program Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow
import matplotlib.pyplot as plt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
