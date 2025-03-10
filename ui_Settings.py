# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings.ui'
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
    QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_Dialog_settings(object):
    def setupUi(self, Dialog_settings):
        if not Dialog_settings.objectName():
            Dialog_settings.setObjectName(u"Dialog_settings")
        Dialog_settings.resize(621, 409)
        self.gridLayout = QGridLayout(Dialog_settings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox_Settings = QDialogButtonBox(Dialog_settings)
        self.buttonBox_Settings.setObjectName(u"buttonBox_Settings")
        self.buttonBox_Settings.setLocale(QLocale(QLocale.Walloon, QLocale.Belgium))
        self.buttonBox_Settings.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox_Settings.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox_Settings, 2, 1, 1, 1)

        self.pushButton_Restore_Default = QPushButton(Dialog_settings)
        self.pushButton_Restore_Default.setObjectName(u"pushButton_Restore_Default")

        self.gridLayout.addWidget(self.pushButton_Restore_Default, 2, 0, 1, 1)

        self.tabWidget_Settings = QTabWidget(Dialog_settings)
        self.tabWidget_Settings.setObjectName(u"tabWidget_Settings")
        self.General_Settings = QWidget()
        self.General_Settings.setObjectName(u"General_Settings")
        self.gridLayout_2 = QGridLayout(self.General_Settings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_Gen_1 = QHBoxLayout()
        self.horizontalLayout_Gen_1.setObjectName(u"horizontalLayout_Gen_1")
        self.label_Gen_pho = QLabel(self.General_Settings)
        self.label_Gen_pho.setObjectName(u"label_Gen_pho")

        self.horizontalLayout_Gen_1.addWidget(self.label_Gen_pho, 0, Qt.AlignmentFlag.AlignRight)

        self.lineEdit_Gen_pho = QLineEdit(self.General_Settings)
        self.lineEdit_Gen_pho.setObjectName(u"lineEdit_Gen_pho")

        self.horizontalLayout_Gen_1.addWidget(self.lineEdit_Gen_pho, 0, Qt.AlignmentFlag.AlignLeft)


        self.gridLayout_2.addLayout(self.horizontalLayout_Gen_1, 0, 0, 1, 1)

        self.horizontalLayout_Gen_2 = QHBoxLayout()
        self.horizontalLayout_Gen_2.setObjectName(u"horizontalLayout_Gen_2")
        self.label_Gen_Gamut = QLabel(self.General_Settings)
        self.label_Gen_Gamut.setObjectName(u"label_Gen_Gamut")

        self.horizontalLayout_Gen_2.addWidget(self.label_Gen_Gamut, 0, Qt.AlignmentFlag.AlignRight)

        self.comboBox_Gen_Gamut = QComboBox(self.General_Settings)
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.setObjectName(u"comboBox_Gen_Gamut")

        self.horizontalLayout_Gen_2.addWidget(self.comboBox_Gen_Gamut, 0, Qt.AlignmentFlag.AlignLeft)


        self.gridLayout_2.addLayout(self.horizontalLayout_Gen_2, 1, 0, 1, 1)

        self.horizontalLayout_Gen_3 = QHBoxLayout()
        self.horizontalLayout_Gen_3.setObjectName(u"horizontalLayout_Gen_3")
        self.label_Gen_illuminant = QLabel(self.General_Settings)
        self.label_Gen_illuminant.setObjectName(u"label_Gen_illuminant")

        self.horizontalLayout_Gen_3.addWidget(self.label_Gen_illuminant, 0, Qt.AlignmentFlag.AlignRight)

        self.comboBox_Gen_illuminant = QComboBox(self.General_Settings)
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.setObjectName(u"comboBox_Gen_illuminant")

        self.horizontalLayout_Gen_3.addWidget(self.comboBox_Gen_illuminant, 0, Qt.AlignmentFlag.AlignLeft)


        self.gridLayout_2.addLayout(self.horizontalLayout_Gen_3, 2, 0, 1, 1)

        self.horizontalLayout_Gen_4 = QHBoxLayout()
        self.horizontalLayout_Gen_4.setObjectName(u"horizontalLayout_Gen_4")
        self.label_Gen_RGB = QLabel(self.General_Settings)
        self.label_Gen_RGB.setObjectName(u"label_Gen_RGB")

        self.horizontalLayout_Gen_4.addWidget(self.label_Gen_RGB, 0, Qt.AlignmentFlag.AlignRight)

        self.comboBox_Gen_RGB = QComboBox(self.General_Settings)
        self.comboBox_Gen_RGB.addItem("")
        self.comboBox_Gen_RGB.addItem("")
        self.comboBox_Gen_RGB.setObjectName(u"comboBox_Gen_RGB")

        self.horizontalLayout_Gen_4.addWidget(self.comboBox_Gen_RGB, 0, Qt.AlignmentFlag.AlignLeft)


        self.gridLayout_2.addLayout(self.horizontalLayout_Gen_4, 3, 0, 1, 1)

        self.tabWidget_Settings.addTab(self.General_Settings, "")
        self.Plot_Settings = QWidget()
        self.Plot_Settings.setObjectName(u"Plot_Settings")
        self.verticalLayout_7 = QVBoxLayout(self.Plot_Settings)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_Plot_1 = QHBoxLayout()
        self.horizontalLayout_Plot_1.setObjectName(u"horizontalLayout_Plot_1")
        self.label_Plot_Resolution = QLabel(self.Plot_Settings)
        self.label_Plot_Resolution.setObjectName(u"label_Plot_Resolution")

        self.horizontalLayout_Plot_1.addWidget(self.label_Plot_Resolution)

        self.comboBox_Plot_Resolution = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_Resolution.setObjectName(u"comboBox_Plot_Resolution")

        self.horizontalLayout_Plot_1.addWidget(self.comboBox_Plot_Resolution)

        self.label_Plot_illuminant = QLabel(self.Plot_Settings)
        self.label_Plot_illuminant.setObjectName(u"label_Plot_illuminant")

        self.horizontalLayout_Plot_1.addWidget(self.label_Plot_illuminant)

        self.comboBox_Plot_illuminant = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_illuminant.setObjectName(u"comboBox_Plot_illuminant")

        self.horizontalLayout_Plot_1.addWidget(self.comboBox_Plot_illuminant)

        self.label_Plot_Gamut = QLabel(self.Plot_Settings)
        self.label_Plot_Gamut.setObjectName(u"label_Plot_Gamut")

        self.horizontalLayout_Plot_1.addWidget(self.label_Plot_Gamut)

        self.comboBox_Plot_Gamut = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_Gamut.setObjectName(u"comboBox_Plot_Gamut")

        self.horizontalLayout_Plot_1.addWidget(self.comboBox_Plot_Gamut)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_1)

        self.horizontalLayout_Plot_2 = QHBoxLayout()
        self.horizontalLayout_Plot_2.setObjectName(u"horizontalLayout_Plot_2")
        self.label_Plot_Reflectance = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance.setObjectName(u"label_Plot_Reflectance")

        self.horizontalLayout_Plot_2.addWidget(self.label_Plot_Reflectance)

        self.label_Plot_CIExy = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy.setObjectName(u"label_Plot_CIExy")

        self.horizontalLayout_Plot_2.addWidget(self.label_Plot_CIExy)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_2)

        self.horizontalLayout_Plot_3 = QHBoxLayout()
        self.horizontalLayout_Plot_3.setObjectName(u"horizontalLayout_Plot_3")
        self.label_Plot_Reflectance_Width = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Width.setObjectName(u"label_Plot_Reflectance_Width")

        self.horizontalLayout_Plot_3.addWidget(self.label_Plot_Reflectance_Width)

        self.lineEdit_Plot_Reflectance_Width = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_Reflectance_Width.setObjectName(u"lineEdit_Plot_Reflectance_Width")

        self.horizontalLayout_Plot_3.addWidget(self.lineEdit_Plot_Reflectance_Width)

        self.label_Plot_Reflectance_Width_pixels = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Width_pixels.setObjectName(u"label_Plot_Reflectance_Width_pixels")

        self.horizontalLayout_Plot_3.addWidget(self.label_Plot_Reflectance_Width_pixels)

        self.label_Plot_CIExy_Width = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Width.setObjectName(u"label_Plot_CIExy_Width")

        self.horizontalLayout_Plot_3.addWidget(self.label_Plot_CIExy_Width)

        self.lineEdit_Plot_CIExy_Width = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_CIExy_Width.setObjectName(u"lineEdit_Plot_CIExy_Width")

        self.horizontalLayout_Plot_3.addWidget(self.lineEdit_Plot_CIExy_Width)

        self.label_Plot_CIExy_Width_pixels = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Width_pixels.setObjectName(u"label_Plot_CIExy_Width_pixels")

        self.horizontalLayout_Plot_3.addWidget(self.label_Plot_CIExy_Width_pixels)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_3)

        self.horizontalLayout_Plot_4 = QHBoxLayout()
        self.horizontalLayout_Plot_4.setObjectName(u"horizontalLayout_Plot_4")
        self.label_Plot_Reflectance_Height = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Height.setObjectName(u"label_Plot_Reflectance_Height")

        self.horizontalLayout_Plot_4.addWidget(self.label_Plot_Reflectance_Height)

        self.lineEdit_Plot_Reflectance_Height = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_Reflectance_Height.setObjectName(u"lineEdit_Plot_Reflectance_Height")

        self.horizontalLayout_Plot_4.addWidget(self.lineEdit_Plot_Reflectance_Height)

        self.label_Plot_CIExy_Reflectance_pixels = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Reflectance_pixels.setObjectName(u"label_Plot_CIExy_Reflectance_pixels")

        self.horizontalLayout_Plot_4.addWidget(self.label_Plot_CIExy_Reflectance_pixels)

        self.label_Plot_CIExy_Height = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Height.setObjectName(u"label_Plot_CIExy_Height")

        self.horizontalLayout_Plot_4.addWidget(self.label_Plot_CIExy_Height)

        self.lineEdit_Plot_CIExy_Height = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_CIExy_Height.setObjectName(u"lineEdit_Plot_CIExy_Height")

        self.horizontalLayout_Plot_4.addWidget(self.lineEdit_Plot_CIExy_Height)

        self.label_Plot_CIExy_Height_pixels = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Height_pixels.setObjectName(u"label_Plot_CIExy_Height_pixels")

        self.horizontalLayout_Plot_4.addWidget(self.label_Plot_CIExy_Height_pixels)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_4)

        self.horizontalLayout_Plot_5 = QHBoxLayout()
        self.horizontalLayout_Plot_5.setObjectName(u"horizontalLayout_Plot_5")
        self.label_Plot_Reflectance_Insert_Title = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Insert_Title.setObjectName(u"label_Plot_Reflectance_Insert_Title")

        self.horizontalLayout_Plot_5.addWidget(self.label_Plot_Reflectance_Insert_Title)

        self.comboBox_Plot_Reflectance_Insert_Title = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_Reflectance_Insert_Title.setObjectName(u"comboBox_Plot_Reflectance_Insert_Title")

        self.horizontalLayout_Plot_5.addWidget(self.comboBox_Plot_Reflectance_Insert_Title)

        self.label_Plot_CIExy_Insert_Title = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Insert_Title.setObjectName(u"label_Plot_CIExy_Insert_Title")

        self.horizontalLayout_Plot_5.addWidget(self.label_Plot_CIExy_Insert_Title)

        self.comboBox_Plot_CIExy_Insert_Title = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_CIExy_Insert_Title.setObjectName(u"comboBox_Plot_CIExy_Insert_Title")

        self.horizontalLayout_Plot_5.addWidget(self.comboBox_Plot_CIExy_Insert_Title)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_5)

        self.horizontalLayout_Plot_6 = QHBoxLayout()
        self.horizontalLayout_Plot_6.setObjectName(u"horizontalLayout_Plot_6")
        self.label_Plot_Reflectance_Title = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Title.setObjectName(u"label_Plot_Reflectance_Title")

        self.horizontalLayout_Plot_6.addWidget(self.label_Plot_Reflectance_Title)

        self.lineEdit_Plot_Reflectance_Title = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_Reflectance_Title.setObjectName(u"lineEdit_Plot_Reflectance_Title")

        self.horizontalLayout_Plot_6.addWidget(self.lineEdit_Plot_Reflectance_Title)

        self.label_Plot_CIExy_Title = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Title.setObjectName(u"label_Plot_CIExy_Title")

        self.horizontalLayout_Plot_6.addWidget(self.label_Plot_CIExy_Title)

        self.lineEdit_Plot_CIExy_Title = QLineEdit(self.Plot_Settings)
        self.lineEdit_Plot_CIExy_Title.setObjectName(u"lineEdit_Plot_CIExy_Title")

        self.horizontalLayout_Plot_6.addWidget(self.lineEdit_Plot_CIExy_Title)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_6)

        self.horizontalLayout_Plot_7 = QHBoxLayout()
        self.horizontalLayout_Plot_7.setObjectName(u"horizontalLayout_Plot_7")
        self.label_Plot_Reflectance_Insert_Legend = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance_Insert_Legend.setObjectName(u"label_Plot_Reflectance_Insert_Legend")

        self.horizontalLayout_Plot_7.addWidget(self.label_Plot_Reflectance_Insert_Legend)

        self.comboBox_Plot_Reflectance_Insert_Legend = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_Reflectance_Insert_Legend.setObjectName(u"comboBox_Plot_Reflectance_Insert_Legend")

        self.horizontalLayout_Plot_7.addWidget(self.comboBox_Plot_Reflectance_Insert_Legend, 0, Qt.AlignmentFlag.AlignLeft)

        self.label_Plot_CIExy_Insert_Legend = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy_Insert_Legend.setObjectName(u"label_Plot_CIExy_Insert_Legend")

        self.horizontalLayout_Plot_7.addWidget(self.label_Plot_CIExy_Insert_Legend)

        self.comboBox_Plot_CIExy_Insert_Legend = QComboBox(self.Plot_Settings)
        self.comboBox_Plot_CIExy_Insert_Legend.setObjectName(u"comboBox_Plot_CIExy_Insert_Legend")

        self.horizontalLayout_Plot_7.addWidget(self.comboBox_Plot_CIExy_Insert_Legend, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_7.addLayout(self.horizontalLayout_Plot_7)

        self.tabWidget_Settings.addTab(self.Plot_Settings, "")
        self.Export_Settings = QWidget()
        self.Export_Settings.setObjectName(u"Export_Settings")
        self.verticalLayout_8 = QVBoxLayout(self.Export_Settings)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_Exp_1 = QHBoxLayout()
        self.horizontalLayout_Exp_1.setObjectName(u"horizontalLayout_Exp_1")
        self.label_Export_Separator = QLabel(self.Export_Settings)
        self.label_Export_Separator.setObjectName(u"label_Export_Separator")

        self.horizontalLayout_Exp_1.addWidget(self.label_Export_Separator, 0, Qt.AlignmentFlag.AlignRight)

        self.comboBox_Export_Separator = QComboBox(self.Export_Settings)
        self.comboBox_Export_Separator.addItem("")
        self.comboBox_Export_Separator.addItem("")
        self.comboBox_Export_Separator.setObjectName(u"comboBox_Export_Separator")

        self.horizontalLayout_Exp_1.addWidget(self.comboBox_Export_Separator, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_8.addLayout(self.horizontalLayout_Exp_1)

        self.horizontalLayout_Exp_2 = QHBoxLayout()
        self.horizontalLayout_Exp_2.setObjectName(u"horizontalLayout_Exp_2")
        self.label_Copy_Header = QLabel(self.Export_Settings)
        self.label_Copy_Header.setObjectName(u"label_Copy_Header")

        self.horizontalLayout_Exp_2.addWidget(self.label_Copy_Header, 0, Qt.AlignmentFlag.AlignRight)

        self.comboBox_Copy_Header = QComboBox(self.Export_Settings)
        self.comboBox_Copy_Header.addItem("")
        self.comboBox_Copy_Header.addItem("")
        self.comboBox_Copy_Header.setObjectName(u"comboBox_Copy_Header")

        self.horizontalLayout_Exp_2.addWidget(self.comboBox_Copy_Header, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_8.addLayout(self.horizontalLayout_Exp_2)

        self.tabWidget_Settings.addTab(self.Export_Settings, "")

        self.gridLayout.addWidget(self.tabWidget_Settings, 0, 0, 1, 2)


        self.retranslateUi(Dialog_settings)
        self.buttonBox_Settings.accepted.connect(Dialog_settings.accept)
        self.buttonBox_Settings.rejected.connect(Dialog_settings.reject)

        self.tabWidget_Settings.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Dialog_settings)
    # setupUi

    def retranslateUi(self, Dialog_settings):
        Dialog_settings.setWindowTitle(QCoreApplication.translate("Dialog_settings", u"Dialog", None))
        self.pushButton_Restore_Default.setText(QCoreApplication.translate("Dialog_settings", u"Restore Default", None))
        self.label_Gen_pho.setText(QCoreApplication.translate("Dialog_settings", u"\u03c1\u2099(\u03bb)", None))
        self.label_Gen_Gamut.setText(QCoreApplication.translate("Dialog_settings", u"Standard Gamut", None))
        self.comboBox_Gen_Gamut.setItemText(0, QCoreApplication.translate("Dialog_settings", u"None", None))
        self.comboBox_Gen_Gamut.setItemText(1, QCoreApplication.translate("Dialog_settings", u"sRGB", None))
        self.comboBox_Gen_Gamut.setItemText(2, QCoreApplication.translate("Dialog_settings", u"Adobe RGB", None))
        self.comboBox_Gen_Gamut.setItemText(3, QCoreApplication.translate("Dialog_settings", u"HTC Vive Pro Eye", None))
        self.comboBox_Gen_Gamut.setItemText(4, QCoreApplication.translate("Dialog_settings", u"Oculus Rift", None))
        self.comboBox_Gen_Gamut.setItemText(5, QCoreApplication.translate("Dialog_settings", u"Oculus Quest", None))
        self.comboBox_Gen_Gamut.setItemText(6, QCoreApplication.translate("Dialog_settings", u"Oculus Quest 2", None))

        self.label_Gen_illuminant.setText(QCoreApplication.translate("Dialog_settings", u"Standard Illuminant", None))
        self.comboBox_Gen_illuminant.setItemText(0, QCoreApplication.translate("Dialog_settings", u"D65", None))
        self.comboBox_Gen_illuminant.setItemText(1, QCoreApplication.translate("Dialog_settings", u"D50", None))
        self.comboBox_Gen_illuminant.setItemText(2, QCoreApplication.translate("Dialog_settings", u"A", None))
        self.comboBox_Gen_illuminant.setItemText(3, QCoreApplication.translate("Dialog_settings", u"E", None))

        self.label_Gen_RGB.setText(QCoreApplication.translate("Dialog_settings", u"RGB Values", None))
        self.comboBox_Gen_RGB.setItemText(0, QCoreApplication.translate("Dialog_settings", u"0 ... 255", None))
        self.comboBox_Gen_RGB.setItemText(1, QCoreApplication.translate("Dialog_settings", u"0 ... 1", None))

        self.tabWidget_Settings.setTabText(self.tabWidget_Settings.indexOf(self.General_Settings), QCoreApplication.translate("Dialog_settings", u"General", None))
        self.label_Plot_Resolution.setText(QCoreApplication.translate("Dialog_settings", u"Resolution", None))
        self.label_Plot_illuminant.setText(QCoreApplication.translate("Dialog_settings", u" Illuminant", None))
        self.label_Plot_Gamut.setText(QCoreApplication.translate("Dialog_settings", u"Gamut", None))
        self.label_Plot_Reflectance.setText(QCoreApplication.translate("Dialog_settings", u"Reflectance Plot", None))
        self.label_Plot_CIExy.setText(QCoreApplication.translate("Dialog_settings", u"CIExy Plot", None))
        self.label_Plot_Reflectance_Width.setText(QCoreApplication.translate("Dialog_settings", u"Width", None))
        self.label_Plot_Reflectance_Width_pixels.setText(QCoreApplication.translate("Dialog_settings", u"pixels", None))
        self.label_Plot_CIExy_Width.setText(QCoreApplication.translate("Dialog_settings", u"Width", None))
        self.label_Plot_CIExy_Width_pixels.setText(QCoreApplication.translate("Dialog_settings", u"pixels", None))
        self.label_Plot_Reflectance_Height.setText(QCoreApplication.translate("Dialog_settings", u"Height", None))
        self.label_Plot_CIExy_Reflectance_pixels.setText(QCoreApplication.translate("Dialog_settings", u"pixels", None))
        self.label_Plot_CIExy_Height.setText(QCoreApplication.translate("Dialog_settings", u"Height", None))
        self.label_Plot_CIExy_Height_pixels.setText(QCoreApplication.translate("Dialog_settings", u"pixels", None))
        self.label_Plot_Reflectance_Insert_Title.setText(QCoreApplication.translate("Dialog_settings", u"Insert Title", None))
        self.label_Plot_CIExy_Insert_Title.setText(QCoreApplication.translate("Dialog_settings", u"Insert Title", None))
        self.label_Plot_Reflectance_Title.setText(QCoreApplication.translate("Dialog_settings", u"Title", None))
        self.label_Plot_CIExy_Title.setText(QCoreApplication.translate("Dialog_settings", u"Title", None))
        self.label_Plot_Reflectance_Insert_Legend.setText(QCoreApplication.translate("Dialog_settings", u"Insert Legend", None))
        self.label_Plot_CIExy_Insert_Legend.setText(QCoreApplication.translate("Dialog_settings", u"Insert Legend", None))
        self.tabWidget_Settings.setTabText(self.tabWidget_Settings.indexOf(self.Plot_Settings), QCoreApplication.translate("Dialog_settings", u"Plot", None))
        self.label_Export_Separator.setText(QCoreApplication.translate("Dialog_settings", u"Export Number Separator", None))
        self.comboBox_Export_Separator.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Comma", None))
        self.comboBox_Export_Separator.setItemText(1, QCoreApplication.translate("Dialog_settings", u"Point", None))

        self.label_Copy_Header.setText(QCoreApplication.translate("Dialog_settings", u"Copy Header to Clipboard", None))
        self.comboBox_Copy_Header.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Yes", None))
        self.comboBox_Copy_Header.setItemText(1, QCoreApplication.translate("Dialog_settings", u"No", None))

        self.tabWidget_Settings.setTabText(self.tabWidget_Settings.indexOf(self.Export_Settings), QCoreApplication.translate("Dialog_settings", u"Export", None))
    # retranslateUi

