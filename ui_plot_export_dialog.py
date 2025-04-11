# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_export_dialog.ui'
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

class Ui_Dialog_plot_export(object):
    def setupUi(self, Dialog_plot_export):
        if not Dialog_plot_export.objectName():
            Dialog_plot_export.setObjectName(u"Dialog_plot_export")
        Dialog_plot_export.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Dialog_plot_export)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_Export_Options = QGroupBox(Dialog_plot_export)
        self.groupBox_Export_Options.setObjectName(u"groupBox_Export_Options")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_Export_Options)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox_Export_Reflectance = QCheckBox(self.groupBox_Export_Options)
        self.checkBox_Export_Reflectance.setObjectName(u"checkBox_Export_Reflectance")
        self.checkBox_Export_Reflectance.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Export_Reflectance)

        self.checkBox_Export_CIE = QCheckBox(self.groupBox_Export_Options)
        self.checkBox_Export_CIE.setObjectName(u"checkBox_Export_CIE")
        self.checkBox_Export_CIE.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Export_CIE)


        self.verticalLayout.addWidget(self.groupBox_Export_Options)

        self.groupBox_Export_File = QGroupBox(Dialog_plot_export)
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

        self.label_Export_Directory = QLabel(self.groupBox_Export_File)
        self.label_Export_Directory.setObjectName(u"label_Export_Directory")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_Export_Directory)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_Export_Directory = QLineEdit(self.groupBox_Export_File)
        self.lineEdit_Export_Directory.setObjectName(u"lineEdit_Export_Directory")

        self.horizontalLayout.addWidget(self.lineEdit_Export_Directory)

        self.pushButton_Export_Browse = QPushButton(self.groupBox_Export_File)
        self.pushButton_Export_Browse.setObjectName(u"pushButton_Export_Browse")

        self.horizontalLayout.addWidget(self.pushButton_Export_Browse)


        self.formLayout.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBox_Export_File)

        self.groupBox_Export_Filename = QGroupBox(Dialog_plot_export)
        self.groupBox_Export_Filename.setObjectName(u"groupBox_Export_Filename")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_Export_Filename)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lineEdit_Export_Filename = QLineEdit(self.groupBox_Export_Filename)
        self.lineEdit_Export_Filename.setObjectName(u"lineEdit_Export_Filename")

        self.verticalLayout_3.addWidget(self.lineEdit_Export_Filename)


        self.verticalLayout.addWidget(self.groupBox_Export_Filename)

        self.buttonBox = QDialogButtonBox(Dialog_plot_export)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_plot_export)
        self.buttonBox.accepted.connect(Dialog_plot_export.accept)
        self.buttonBox.rejected.connect(Dialog_plot_export.reject)

        QMetaObject.connectSlotsByName(Dialog_plot_export)
    # setupUi

    def retranslateUi(self, Dialog_plot_export):
        Dialog_plot_export.setWindowTitle(QCoreApplication.translate("Dialog_plot_export", u"Export Plots", None))
        self.groupBox_Export_Options.setTitle(QCoreApplication.translate("Dialog_plot_export", u"Export Options", None))
        self.checkBox_Export_Reflectance.setText(QCoreApplication.translate("Dialog_plot_export", u"Reflectance Plot", None))
        self.checkBox_Export_CIE.setText(QCoreApplication.translate("Dialog_plot_export", u"CIE 1931 Chromaticity Plot", None))
        self.groupBox_Export_File.setTitle(QCoreApplication.translate("Dialog_plot_export", u"Export File", None))
        self.label_Export_Format.setText(QCoreApplication.translate("Dialog_plot_export", u"Format:", None))
        self.comboBox_Export_Format.setItemText(0, QCoreApplication.translate("Dialog_plot_export", u"PNG (.png)", None))
        self.comboBox_Export_Format.setItemText(1, QCoreApplication.translate("Dialog_plot_export", u"JPEG (.jpg)", None))
        self.comboBox_Export_Format.setItemText(2, QCoreApplication.translate("Dialog_plot_export", u"TIFF (.tif)", None))
        self.comboBox_Export_Format.setItemText(3, QCoreApplication.translate("Dialog_plot_export", u"PDF (.pdf)", None))

        self.label_Export_Directory.setText(QCoreApplication.translate("Dialog_plot_export", u"Directory:", None))
        self.pushButton_Export_Browse.setText(QCoreApplication.translate("Dialog_plot_export", u"Browse...", None))
        self.groupBox_Export_Filename.setTitle(QCoreApplication.translate("Dialog_plot_export", u"Filename Base", None))
        self.lineEdit_Export_Filename.setText(QCoreApplication.translate("Dialog_plot_export", u"plot_export", None))
    # retranslateUi

