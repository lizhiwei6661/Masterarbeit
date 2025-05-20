# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Import.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGraphicsView, QGridLayout, QGroupBox,
    QListView, QPushButton, QSizePolicy, QWidget)

class Ui_Dialog_import(object):
    def setupUi(self, Dialog_import):
        if not Dialog_import.objectName():
            Dialog_import.setObjectName(u"Dialog_import")
        Dialog_import.resize(619, 417)
        self.gridLayout = QGridLayout(Dialog_import)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_import = QGroupBox(Dialog_import)
        self.groupBox_import.setObjectName(u"groupBox_import")
        self.groupBox_import.setFlat(False)
        self.gridLayout_3 = QGridLayout(self.groupBox_import)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(7)
        self.pushButton_black = QPushButton(self.groupBox_import)
        self.pushButton_black.setObjectName(u"pushButton_black")

        self.gridLayout_3.addWidget(self.pushButton_black, 8, 0, 1, 1)

        self.listView_import_file = QListView(self.groupBox_import)
        self.listView_import_file.setObjectName(u"listView_import_file")
        self.listView_import_file.setMovement(QListView.Movement.Free)
        self.listView_import_file.setProperty(u"isWrapping", False)
        self.listView_import_file.setResizeMode(QListView.ResizeMode.Fixed)
        self.listView_import_file.setLayoutMode(QListView.LayoutMode.SinglePass)

        self.gridLayout_3.addWidget(self.listView_import_file, 12, 1, 1, 1)

        self.comboBox_equp = QComboBox(self.groupBox_import)
        self.comboBox_equp.addItem("")
        self.comboBox_equp.addItem("")
        self.comboBox_equp.setObjectName(u"comboBox_equp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_equp.sizePolicy().hasHeightForWidth())
        self.comboBox_equp.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.comboBox_equp, 4, 0, 1, 1)

        self.pushButton_clear_ref = QPushButton(self.groupBox_import)
        self.pushButton_clear_ref.setObjectName(u"pushButton_clear_ref")
        self.pushButton_clear_ref.setMinimumSize(QSize(0, 0))

        self.gridLayout_3.addWidget(self.pushButton_clear_ref, 10, 0, 1, 1)

        self.view_spec = QGraphicsView(self.groupBox_import)
        self.view_spec.setObjectName(u"view_spec")
        self.view_spec.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addWidget(self.view_spec, 4, 1, 7, 1)

        self.pushButton_white = QPushButton(self.groupBox_import)
        self.pushButton_white.setObjectName(u"pushButton_white")

        self.gridLayout_3.addWidget(self.pushButton_white, 9, 0, 1, 1)

        self.pushButton_select_data = QPushButton(self.groupBox_import)
        self.pushButton_select_data.setObjectName(u"pushButton_select_data")
        sizePolicy.setHeightForWidth(self.pushButton_select_data.sizePolicy().hasHeightForWidth())
        self.pushButton_select_data.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.pushButton_select_data, 12, 0, 1, 1, Qt.AlignmentFlag.AlignTop)

        self.gridLayout_3.setRowMinimumHeight(3, 3)
        self.gridLayout_3.setRowMinimumHeight(4, 3)
        self.gridLayout_3.setRowMinimumHeight(5, 3)
        self.gridLayout_3.setRowMinimumHeight(6, 3)
        self.gridLayout_3.setRowMinimumHeight(7, 3)

        self.gridLayout.addWidget(self.groupBox_import, 1, 0, 1, 1)

        self.buttonBox_import = QDialogButtonBox(Dialog_import)
        self.buttonBox_import.setObjectName(u"buttonBox_import")
        font = QFont()
        font.setFamilies([u".AppleSystemUIFont"])
        self.buttonBox_import.setFont(font)
        self.buttonBox_import.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox_import, 3, 0, 1, 1)


        self.retranslateUi(Dialog_import)

        QMetaObject.connectSlotsByName(Dialog_import)
    # setupUi

    def retranslateUi(self, Dialog_import):
        Dialog_import.setWindowTitle(QCoreApplication.translate("Dialog_import", u"Dialog", None))
        self.groupBox_import.setTitle("")
        self.pushButton_black.setText(QCoreApplication.translate("Dialog_import", u"Select Black Reference", None))
        self.comboBox_equp.setItemText(0, QCoreApplication.translate("Dialog_import", u"Aleksameter", None))
        self.comboBox_equp.setItemText(1, QCoreApplication.translate("Dialog_import", u"Generic", None))

        self.pushButton_clear_ref.setText(QCoreApplication.translate("Dialog_import", u"Clear Reference", None))
        self.pushButton_white.setText(QCoreApplication.translate("Dialog_import", u"Select White Reference", None))
        self.pushButton_select_data.setText(QCoreApplication.translate("Dialog_import", u"Select Measurements", None))
    # retranslateUi

