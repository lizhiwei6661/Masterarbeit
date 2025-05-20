# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_dialog.ui'
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

class Ui_Dialog_plot(object):
    def setupUi(self, Dialog_plot):
        if not Dialog_plot.objectName():
            Dialog_plot.setObjectName(u"Dialog_plot")
        Dialog_plot.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Dialog_plot)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_Plot_Options = QGroupBox(Dialog_plot)
        self.groupBox_Plot_Options.setObjectName(u"groupBox_Plot_Options")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_Plot_Options)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox_Plot_Reflectance = QCheckBox(self.groupBox_Plot_Options)
        self.checkBox_Plot_Reflectance.setObjectName(u"checkBox_Plot_Reflectance")
        self.checkBox_Plot_Reflectance.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Plot_Reflectance)

        self.checkBox_Plot_CIE = QCheckBox(self.groupBox_Plot_Options)
        self.checkBox_Plot_CIE.setObjectName(u"checkBox_Plot_CIE")
        self.checkBox_Plot_CIE.setChecked(True)

        self.verticalLayout_2.addWidget(self.checkBox_Plot_CIE)


        self.verticalLayout.addWidget(self.groupBox_Plot_Options)

        self.groupBox_Plot_File = QGroupBox(Dialog_plot)
        self.groupBox_Plot_File.setObjectName(u"groupBox_Plot_File")
        self.formLayout = QFormLayout(self.groupBox_Plot_File)
        self.formLayout.setObjectName(u"formLayout")
        self.label_Plot_Format = QLabel(self.groupBox_Plot_File)
        self.label_Plot_Format.setObjectName(u"label_Plot_Format")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_Plot_Format)

        self.comboBox_Plot_Format = QComboBox(self.groupBox_Plot_File)
        self.comboBox_Plot_Format.addItem("")
        self.comboBox_Plot_Format.addItem("")
        self.comboBox_Plot_Format.addItem("")
        self.comboBox_Plot_Format.addItem("")
        self.comboBox_Plot_Format.setObjectName(u"comboBox_Plot_Format")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_Plot_Format)

        self.label_Plot_File = QLabel(self.groupBox_Plot_File)
        self.label_Plot_File.setObjectName(u"label_Plot_File")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_Plot_File)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_Plot_File = QLineEdit(self.groupBox_Plot_File)
        self.lineEdit_Plot_File.setObjectName(u"lineEdit_Plot_File")

        self.horizontalLayout.addWidget(self.lineEdit_Plot_File)

        self.pushButton_Plot_Browse = QPushButton(self.groupBox_Plot_File)
        self.pushButton_Plot_Browse.setObjectName(u"pushButton_Plot_Browse")

        self.horizontalLayout.addWidget(self.pushButton_Plot_Browse)


        self.formLayout.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBox_Plot_File)

        self.buttonBox = QDialogButtonBox(Dialog_plot)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog_plot)
        self.buttonBox.accepted.connect(Dialog_plot.accept)
        self.buttonBox.rejected.connect(Dialog_plot.reject)

        QMetaObject.connectSlotsByName(Dialog_plot)
    # setupUi

    def retranslateUi(self, Dialog_plot):
        Dialog_plot.setWindowTitle(QCoreApplication.translate("Dialog_plot", u"Plot Export", None))
        self.groupBox_Plot_Options.setTitle(QCoreApplication.translate("Dialog_plot", u"Plot Options", None))
        self.checkBox_Plot_Reflectance.setText(QCoreApplication.translate("Dialog_plot", u"Reflectance Data", None))
        self.checkBox_Plot_CIE.setText(QCoreApplication.translate("Dialog_plot", u"CIE 1931 Chromaticity", None))
        self.groupBox_Plot_File.setTitle(QCoreApplication.translate("Dialog_plot", u"Export File", None))
        self.label_Plot_Format.setText(QCoreApplication.translate("Dialog_plot", u"Format:", None))
        self.comboBox_Plot_Format.setItemText(0, QCoreApplication.translate("Dialog_plot", u"PNG (.png)", None))
        self.comboBox_Plot_Format.setItemText(1, QCoreApplication.translate("Dialog_plot", u"JPEG (.jpg)", None))
        self.comboBox_Plot_Format.setItemText(2, QCoreApplication.translate("Dialog_plot", u"TIFF (.tif)", None))
        self.comboBox_Plot_Format.setItemText(3, QCoreApplication.translate("Dialog_plot", u"PDF (.pdf)", None))

        self.label_Plot_File.setText(QCoreApplication.translate("Dialog_plot", u"File:", None))
        self.pushButton_Plot_Browse.setText(QCoreApplication.translate("Dialog_plot", u"Browse...", None))
    # retranslateUi

