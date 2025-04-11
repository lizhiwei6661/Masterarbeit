# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dialog_export(object):
    def setupUi(self, Dialog_export):
        if not Dialog_export.objectName():
            Dialog_export.setObjectName(u"Dialog_export")
        Dialog_export.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Dialog_export)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_Export_Options = QGroupBox(Dialog_export)
        self.groupBox_Export_Options.setObjectName(u"groupBox_Export_Options")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_Export_Options)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox_Export_Rho = QCheckBox(self.groupBox_Export_Options)
        self.checkBox_Export_Rho.setObjectName(u"checkBox_Export_Rho")
        self.checkBox_Export_Rho.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Export_Rho)

        self.checkBox_Export_Color = QCheckBox(self.groupBox_Export_Options)
        self.checkBox_Export_Color.setObjectName(u"checkBox_Export_Color")
        self.checkBox_Export_Color.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Export_Color)


        self.verticalLayout.addWidget(self.groupBox_Export_Options)

        self.groupBox_Export_File = QGroupBox(Dialog_export)
        self.groupBox_Export_File.setObjectName(u"groupBox_Export_File")
        self.formLayout = QFormLayout(self.groupBox_Export_File)
        self.formLayout.setObjectName(u"formLayout")
        self.label_Export_Format = QLabel(self.groupBox_Export_File)
        self.label_Export_Format.setObjectName(u"label_Export_Format")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_Export_Format)

        self.comboBox_Export_Format = QComboBox(self.groupBox_Export_File)
        self.comboBox_Export_Format.addItem("")
        self.comboBox_Export_Format.addItem("")
        self.comboBox_Export_Format.addItem("")
        self.comboBox_Export_Format.addItem("")
        self.comboBox_Export_Format.setObjectName(u"comboBox_Export_Format")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_Export_Format)

        self.label_Export_File = QLabel(self.groupBox_Export_File)
        self.label_Export_File.setObjectName(u"label_Export_File")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_Export_File)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_Export_File = QLineEdit(self.groupBox_Export_File)
        self.lineEdit_Export_File.setObjectName(u"lineEdit_Export_File")

        self.horizontalLayout.addWidget(self.lineEdit_Export_File)

        self.pushButton_Export_Browse = QPushButton(self.groupBox_Export_File)
        self.pushButton_Export_Browse.setObjectName(u"pushButton_Export_Browse")

        self.horizontalLayout.addWidget(self.pushButton_Export_Browse)


        self.formLayout.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBox_Export_File)

        self.buttonBox = QDialogButtonBox(Dialog_export)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_export)
        self.buttonBox.accepted.connect(Dialog_export.accept)
        self.buttonBox.rejected.connect(Dialog_export.reject)

        QMetaObject.connectSlotsByName(Dialog_export)
    # setupUi

    def retranslateUi(self, Dialog_export):
        Dialog_export.setWindowTitle(QCoreApplication.translate("Dialog_export", u"Export", None))
        self.groupBox_Export_Options.setTitle(QCoreApplication.translate("Dialog_export", u"Export Options", None))
        self.checkBox_Export_Rho.setText(QCoreApplication.translate("Dialog_export", u"Reflectance Data", None))
        self.checkBox_Export_Color.setText(QCoreApplication.translate("Dialog_export", u"Color Data", None))
        self.groupBox_Export_File.setTitle(QCoreApplication.translate("Dialog_export", u"Export File", None))
        self.label_Export_Format.setText(QCoreApplication.translate("Dialog_export", u"Format:", None))
        self.comboBox_Export_Format.setItemText(0, QCoreApplication.translate("Dialog_export", u"Excel (.xlsx)", None))
        self.comboBox_Export_Format.setItemText(1, QCoreApplication.translate("Dialog_export", u"CSV (.csv)", None))
        self.comboBox_Export_Format.setItemText(2, QCoreApplication.translate("Dialog_export", u"Text (.txt)", None))
        self.comboBox_Export_Format.setItemText(3, QCoreApplication.translate("Dialog_export", u"JSON (.json)", None))

        self.label_Export_File.setText(QCoreApplication.translate("Dialog_export", u"File:", None))
        self.pushButton_Export_Browse.setText(QCoreApplication.translate("Dialog_export", u"Browse...", None))
    # retranslateUi

