# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QDialogButtonBox, QFormLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_Dialog_settings(object):
    def setupUi(self, Dialog_settings):
        if not Dialog_settings.objectName():
            Dialog_settings.setObjectName(u"Dialog_settings")
        Dialog_settings.resize(600, 400)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog_settings.sizePolicy().hasHeightForWidth())
        Dialog_settings.setSizePolicy(sizePolicy)
        Dialog_settings.setMinimumSize(QSize(600, 400))
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
        self.gridLayout_2.setSpacing(10)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.formLayout_Gen = QFormLayout()
        self.formLayout_Gen.setObjectName(u"formLayout_Gen")
        self.formLayout_Gen.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_Gen.setFormAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.formLayout_Gen.setHorizontalSpacing(20)
        self.formLayout_Gen.setVerticalSpacing(30)
        self.formLayout_Gen.setContentsMargins(0, 0, -1, -1)
        self.label_Gen_pho = QLabel(self.General_Settings)
        self.label_Gen_pho.setObjectName(u"label_Gen_pho")
        self.label_Gen_pho.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Gen.setWidget(0, QFormLayout.LabelRole, self.label_Gen_pho)

        self.lineEdit_Gen_pho = QLineEdit(self.General_Settings)
        self.lineEdit_Gen_pho.setObjectName(u"lineEdit_Gen_pho")
        self.lineEdit_Gen_pho.setMinimumSize(QSize(133, 0))
        self.lineEdit_Gen_pho.setMaximumSize(QSize(133, 16777215))

        self.formLayout_Gen.setWidget(0, QFormLayout.FieldRole, self.lineEdit_Gen_pho)

        self.label_Gen_Gamut = QLabel(self.General_Settings)
        self.label_Gen_Gamut.setObjectName(u"label_Gen_Gamut")
        self.label_Gen_Gamut.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Gen.setWidget(1, QFormLayout.LabelRole, self.label_Gen_Gamut)

        self.comboBox_Gen_Gamut = QComboBox(self.General_Settings)
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.addItem("")
        self.comboBox_Gen_Gamut.setObjectName(u"comboBox_Gen_Gamut")
        self.comboBox_Gen_Gamut.setMinimumSize(QSize(150, 0))
        self.comboBox_Gen_Gamut.setMaximumSize(QSize(150, 16777215))

        self.formLayout_Gen.setWidget(1, QFormLayout.FieldRole, self.comboBox_Gen_Gamut)

        self.label_Gen_illuminant = QLabel(self.General_Settings)
        self.label_Gen_illuminant.setObjectName(u"label_Gen_illuminant")
        self.label_Gen_illuminant.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Gen.setWidget(2, QFormLayout.LabelRole, self.label_Gen_illuminant)

        self.comboBox_Gen_illuminant = QComboBox(self.General_Settings)
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.addItem("")
        self.comboBox_Gen_illuminant.setObjectName(u"comboBox_Gen_illuminant")
        self.comboBox_Gen_illuminant.setMinimumSize(QSize(150, 0))
        self.comboBox_Gen_illuminant.setMaximumSize(QSize(150, 16777215))

        self.formLayout_Gen.setWidget(2, QFormLayout.FieldRole, self.comboBox_Gen_illuminant)

        self.label_Gen_RGB = QLabel(self.General_Settings)
        self.label_Gen_RGB.setObjectName(u"label_Gen_RGB")
        self.label_Gen_RGB.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Gen.setWidget(3, QFormLayout.LabelRole, self.label_Gen_RGB)

        self.comboBox_Gen_RGB = QComboBox(self.General_Settings)
        self.comboBox_Gen_RGB.addItem("")
        self.comboBox_Gen_RGB.addItem("")
        self.comboBox_Gen_RGB.setObjectName(u"comboBox_Gen_RGB")
        self.comboBox_Gen_RGB.setMinimumSize(QSize(150, 0))
        self.comboBox_Gen_RGB.setMaximumSize(QSize(150, 16777215))

        self.formLayout_Gen.setWidget(3, QFormLayout.FieldRole, self.comboBox_Gen_RGB)


        self.gridLayout_2.addLayout(self.formLayout_Gen, 0, 0, 1, 1)

        self.tabWidget_Settings.addTab(self.General_Settings, "")
        self.Plot_Settings = QWidget()
        self.Plot_Settings.setObjectName(u"Plot_Settings")
        self.verticalLayout_Plot = QVBoxLayout(self.Plot_Settings)
        self.verticalLayout_Plot.setSpacing(0)
        self.verticalLayout_Plot.setObjectName(u"verticalLayout_Plot")
        self.verticalLayout_Plot.setContentsMargins(20, 0, 20, 20)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(40)
        self.gridLayout_3.setVerticalSpacing(10)
        self.label_Plot_Reflectance = QLabel(self.Plot_Settings)
        self.label_Plot_Reflectance.setObjectName(u"label_Plot_Reflectance")
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        self.label_Plot_Reflectance.setFont(font)
        self.label_Plot_Reflectance.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label_Plot_Reflectance, 0, 0, 1, 1, Qt.AlignCenter)

        self.label_Plot_CIExy = QLabel(self.Plot_Settings)
        self.label_Plot_CIExy.setObjectName(u"label_Plot_CIExy")
        self.label_Plot_CIExy.setFont(font)
        self.label_Plot_CIExy.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label_Plot_CIExy, 0, 1, 1, 1, Qt.AlignCenter)

        self.widget_reflectance = QWidget(self.Plot_Settings)
        self.widget_reflectance.setObjectName(u"widget_reflectance")
        self.formLayout_Reflectance = QFormLayout(self.widget_reflectance)
        self.formLayout_Reflectance.setObjectName(u"formLayout_Reflectance")
        self.formLayout_Reflectance.setHorizontalSpacing(10)
        self.formLayout_Reflectance.setVerticalSpacing(20)
        self.label_Plot_Reflectance_Width = QLabel(self.widget_reflectance)
        self.label_Plot_Reflectance_Width.setObjectName(u"label_Plot_Reflectance_Width")
        self.label_Plot_Reflectance_Width.setMinimumSize(QSize(80, 0))

        self.formLayout_Reflectance.setWidget(0, QFormLayout.LabelRole, self.label_Plot_Reflectance_Width)

        self.lineEdit_Plot_Reflectance_Width = QLineEdit(self.widget_reflectance)
        self.lineEdit_Plot_Reflectance_Width.setObjectName(u"lineEdit_Plot_Reflectance_Width")
        self.lineEdit_Plot_Reflectance_Width.setMinimumSize(QSize(60, 25))
        self.lineEdit_Plot_Reflectance_Width.setMaximumSize(QSize(60, 25))

        self.formLayout_Reflectance.setWidget(0, QFormLayout.FieldRole, self.lineEdit_Plot_Reflectance_Width)

        self.label_Plot_Reflectance_Height = QLabel(self.widget_reflectance)
        self.label_Plot_Reflectance_Height.setObjectName(u"label_Plot_Reflectance_Height")
        self.label_Plot_Reflectance_Height.setMinimumSize(QSize(80, 0))

        self.formLayout_Reflectance.setWidget(1, QFormLayout.LabelRole, self.label_Plot_Reflectance_Height)

        self.lineEdit_Plot_Reflectance_Height = QLineEdit(self.widget_reflectance)
        self.lineEdit_Plot_Reflectance_Height.setObjectName(u"lineEdit_Plot_Reflectance_Height")
        self.lineEdit_Plot_Reflectance_Height.setMinimumSize(QSize(60, 25))
        self.lineEdit_Plot_Reflectance_Height.setMaximumSize(QSize(60, 25))

        self.formLayout_Reflectance.setWidget(1, QFormLayout.FieldRole, self.lineEdit_Plot_Reflectance_Height)

        self.label_Plot_Reflectance_Insert_Title = QLabel(self.widget_reflectance)
        self.label_Plot_Reflectance_Insert_Title.setObjectName(u"label_Plot_Reflectance_Insert_Title")
        self.label_Plot_Reflectance_Insert_Title.setMinimumSize(QSize(80, 0))

        self.formLayout_Reflectance.setWidget(2, QFormLayout.LabelRole, self.label_Plot_Reflectance_Insert_Title)

        self.comboBox_Plot_Reflectance_Insert_Title = QComboBox(self.widget_reflectance)
        self.comboBox_Plot_Reflectance_Insert_Title.addItem("")
        self.comboBox_Plot_Reflectance_Insert_Title.addItem("")
        self.comboBox_Plot_Reflectance_Insert_Title.setObjectName(u"comboBox_Plot_Reflectance_Insert_Title")
        self.comboBox_Plot_Reflectance_Insert_Title.setMinimumSize(QSize(70, 25))
        self.comboBox_Plot_Reflectance_Insert_Title.setMaximumSize(QSize(70, 25))

        self.formLayout_Reflectance.setWidget(2, QFormLayout.FieldRole, self.comboBox_Plot_Reflectance_Insert_Title)

        self.label_Plot_Reflectance_Title = QLabel(self.widget_reflectance)
        self.label_Plot_Reflectance_Title.setObjectName(u"label_Plot_Reflectance_Title")
        self.label_Plot_Reflectance_Title.setMinimumSize(QSize(80, 0))

        self.formLayout_Reflectance.setWidget(3, QFormLayout.LabelRole, self.label_Plot_Reflectance_Title)

        self.lineEdit_Plot_Reflectance_Title = QLineEdit(self.widget_reflectance)
        self.lineEdit_Plot_Reflectance_Title.setObjectName(u"lineEdit_Plot_Reflectance_Title")
        self.lineEdit_Plot_Reflectance_Title.setMinimumSize(QSize(150, 25))

        self.formLayout_Reflectance.setWidget(3, QFormLayout.FieldRole, self.lineEdit_Plot_Reflectance_Title)

        self.label_Plot_Reflectance_Insert_Legend = QLabel(self.widget_reflectance)
        self.label_Plot_Reflectance_Insert_Legend.setObjectName(u"label_Plot_Reflectance_Insert_Legend")
        self.label_Plot_Reflectance_Insert_Legend.setMinimumSize(QSize(80, 0))

        self.formLayout_Reflectance.setWidget(4, QFormLayout.LabelRole, self.label_Plot_Reflectance_Insert_Legend)

        self.comboBox_Plot_Reflectance_Insert_Legend = QComboBox(self.widget_reflectance)
        self.comboBox_Plot_Reflectance_Insert_Legend.addItem("")
        self.comboBox_Plot_Reflectance_Insert_Legend.addItem("")
        self.comboBox_Plot_Reflectance_Insert_Legend.setObjectName(u"comboBox_Plot_Reflectance_Insert_Legend")
        self.comboBox_Plot_Reflectance_Insert_Legend.setMinimumSize(QSize(70, 25))
        self.comboBox_Plot_Reflectance_Insert_Legend.setMaximumSize(QSize(70, 25))

        self.formLayout_Reflectance.setWidget(4, QFormLayout.FieldRole, self.comboBox_Plot_Reflectance_Insert_Legend)


        self.gridLayout_3.addWidget(self.widget_reflectance, 1, 0, 1, 1)

        self.widget_ciexy = QWidget(self.Plot_Settings)
        self.widget_ciexy.setObjectName(u"widget_ciexy")
        self.formLayout_CIExy = QFormLayout(self.widget_ciexy)
        self.formLayout_CIExy.setObjectName(u"formLayout_CIExy")
        self.formLayout_CIExy.setHorizontalSpacing(10)
        self.formLayout_CIExy.setVerticalSpacing(20)
        self.label_Plot_CIExy_Width = QLabel(self.widget_ciexy)
        self.label_Plot_CIExy_Width.setObjectName(u"label_Plot_CIExy_Width")
        self.label_Plot_CIExy_Width.setMinimumSize(QSize(80, 0))

        self.formLayout_CIExy.setWidget(0, QFormLayout.LabelRole, self.label_Plot_CIExy_Width)

        self.lineEdit_Plot_CIExy_Width = QLineEdit(self.widget_ciexy)
        self.lineEdit_Plot_CIExy_Width.setObjectName(u"lineEdit_Plot_CIExy_Width")
        self.lineEdit_Plot_CIExy_Width.setMinimumSize(QSize(60, 25))
        self.lineEdit_Plot_CIExy_Width.setMaximumSize(QSize(60, 25))

        self.formLayout_CIExy.setWidget(0, QFormLayout.FieldRole, self.lineEdit_Plot_CIExy_Width)

        self.label_Plot_CIExy_Height = QLabel(self.widget_ciexy)
        self.label_Plot_CIExy_Height.setObjectName(u"label_Plot_CIExy_Height")
        self.label_Plot_CIExy_Height.setMinimumSize(QSize(80, 0))

        self.formLayout_CIExy.setWidget(1, QFormLayout.LabelRole, self.label_Plot_CIExy_Height)

        self.lineEdit_Plot_CIExy_Height = QLineEdit(self.widget_ciexy)
        self.lineEdit_Plot_CIExy_Height.setObjectName(u"lineEdit_Plot_CIExy_Height")
        self.lineEdit_Plot_CIExy_Height.setMinimumSize(QSize(60, 25))
        self.lineEdit_Plot_CIExy_Height.setMaximumSize(QSize(60, 25))

        self.formLayout_CIExy.setWidget(1, QFormLayout.FieldRole, self.lineEdit_Plot_CIExy_Height)

        self.label_Plot_CIExy_Insert_Title = QLabel(self.widget_ciexy)
        self.label_Plot_CIExy_Insert_Title.setObjectName(u"label_Plot_CIExy_Insert_Title")
        self.label_Plot_CIExy_Insert_Title.setMinimumSize(QSize(80, 0))

        self.formLayout_CIExy.setWidget(2, QFormLayout.LabelRole, self.label_Plot_CIExy_Insert_Title)

        self.comboBox_Plot_CIExy_Insert_Title = QComboBox(self.widget_ciexy)
        self.comboBox_Plot_CIExy_Insert_Title.addItem("")
        self.comboBox_Plot_CIExy_Insert_Title.addItem("")
        self.comboBox_Plot_CIExy_Insert_Title.setObjectName(u"comboBox_Plot_CIExy_Insert_Title")
        self.comboBox_Plot_CIExy_Insert_Title.setMinimumSize(QSize(70, 25))
        self.comboBox_Plot_CIExy_Insert_Title.setMaximumSize(QSize(70, 25))

        self.formLayout_CIExy.setWidget(2, QFormLayout.FieldRole, self.comboBox_Plot_CIExy_Insert_Title)

        self.label_Plot_CIExy_Title = QLabel(self.widget_ciexy)
        self.label_Plot_CIExy_Title.setObjectName(u"label_Plot_CIExy_Title")
        self.label_Plot_CIExy_Title.setMinimumSize(QSize(80, 0))

        self.formLayout_CIExy.setWidget(3, QFormLayout.LabelRole, self.label_Plot_CIExy_Title)

        self.lineEdit_Plot_CIExy_Title = QLineEdit(self.widget_ciexy)
        self.lineEdit_Plot_CIExy_Title.setObjectName(u"lineEdit_Plot_CIExy_Title")
        self.lineEdit_Plot_CIExy_Title.setMinimumSize(QSize(150, 25))

        self.formLayout_CIExy.setWidget(3, QFormLayout.FieldRole, self.lineEdit_Plot_CIExy_Title)

        self.label_Plot_CIExy_Insert_Legend = QLabel(self.widget_ciexy)
        self.label_Plot_CIExy_Insert_Legend.setObjectName(u"label_Plot_CIExy_Insert_Legend")
        self.label_Plot_CIExy_Insert_Legend.setMinimumSize(QSize(80, 0))

        self.formLayout_CIExy.setWidget(4, QFormLayout.LabelRole, self.label_Plot_CIExy_Insert_Legend)

        self.comboBox_Plot_CIExy_Insert_Legend = QComboBox(self.widget_ciexy)
        self.comboBox_Plot_CIExy_Insert_Legend.addItem("")
        self.comboBox_Plot_CIExy_Insert_Legend.addItem("")
        self.comboBox_Plot_CIExy_Insert_Legend.setObjectName(u"comboBox_Plot_CIExy_Insert_Legend")
        self.comboBox_Plot_CIExy_Insert_Legend.setMinimumSize(QSize(70, 25))
        self.comboBox_Plot_CIExy_Insert_Legend.setMaximumSize(QSize(70, 25))

        self.formLayout_CIExy.setWidget(4, QFormLayout.FieldRole, self.comboBox_Plot_CIExy_Insert_Legend)


        self.gridLayout_3.addWidget(self.widget_ciexy, 1, 1, 1, 1)


        self.verticalLayout_Plot.addLayout(self.gridLayout_3)

        self.tabWidget_Settings.addTab(self.Plot_Settings, "")
        self.Export_Settings = QWidget()
        self.Export_Settings.setObjectName(u"Export_Settings")
        self.gridLayout_4 = QGridLayout(self.Export_Settings)
        self.gridLayout_4.setSpacing(10)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.formLayout_Export = QFormLayout()
        self.formLayout_Export.setObjectName(u"formLayout_Export")
        self.formLayout_Export.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_Export.setFormAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.formLayout_Export.setHorizontalSpacing(20)
        self.formLayout_Export.setVerticalSpacing(30)
        self.formLayout_Export.setContentsMargins(0, 0, -1, -1)
        self.label_Export_Separator = QLabel(self.Export_Settings)
        self.label_Export_Separator.setObjectName(u"label_Export_Separator")
        self.label_Export_Separator.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Export.setWidget(0, QFormLayout.LabelRole, self.label_Export_Separator)

        self.comboBox_Export_Separator = QComboBox(self.Export_Settings)
        self.comboBox_Export_Separator.addItem("")
        self.comboBox_Export_Separator.addItem("")
        self.comboBox_Export_Separator.setObjectName(u"comboBox_Export_Separator")
        self.comboBox_Export_Separator.setMinimumSize(QSize(120, 0))
        self.comboBox_Export_Separator.setMaximumSize(QSize(120, 16777215))

        self.formLayout_Export.setWidget(0, QFormLayout.FieldRole, self.comboBox_Export_Separator)

        self.label_Copy_Header = QLabel(self.Export_Settings)
        self.label_Copy_Header.setObjectName(u"label_Copy_Header")
        self.label_Copy_Header.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_Export.setWidget(1, QFormLayout.LabelRole, self.label_Copy_Header)

        self.comboBox_Copy_Header = QComboBox(self.Export_Settings)
        self.comboBox_Copy_Header.addItem("")
        self.comboBox_Copy_Header.addItem("")
        self.comboBox_Copy_Header.setObjectName(u"comboBox_Copy_Header")
        self.comboBox_Copy_Header.setMinimumSize(QSize(120, 0))
        self.comboBox_Copy_Header.setMaximumSize(QSize(120, 16777215))

        self.formLayout_Export.setWidget(1, QFormLayout.FieldRole, self.comboBox_Copy_Header)


        self.gridLayout_4.addLayout(self.formLayout_Export, 0, 0, 1, 1)

        self.tabWidget_Settings.addTab(self.Export_Settings, "")

        self.gridLayout.addWidget(self.tabWidget_Settings, 0, 0, 1, 2)


        self.retranslateUi(Dialog_settings)
        self.buttonBox_Settings.accepted.connect(Dialog_settings.accept)
        self.buttonBox_Settings.rejected.connect(Dialog_settings.reject)

        self.tabWidget_Settings.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog_settings)
    # setupUi

    def retranslateUi(self, Dialog_settings):
        Dialog_settings.setWindowTitle(QCoreApplication.translate("Dialog_settings", u"Settings", None))
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
        self.label_Plot_Reflectance.setText(QCoreApplication.translate("Dialog_settings", u"Reflectance Plot", None))
        self.label_Plot_CIExy.setText(QCoreApplication.translate("Dialog_settings", u"CIExy Plot", None))
        self.label_Plot_Reflectance_Width.setText(QCoreApplication.translate("Dialog_settings", u"Width (px)", None))
        self.label_Plot_Reflectance_Height.setText(QCoreApplication.translate("Dialog_settings", u"Height (px)", None))
        self.label_Plot_Reflectance_Insert_Title.setText(QCoreApplication.translate("Dialog_settings", u"Insert Title", None))
        self.comboBox_Plot_Reflectance_Insert_Title.setItemText(0, QCoreApplication.translate("Dialog_settings", u"No", None))
        self.comboBox_Plot_Reflectance_Insert_Title.setItemText(1, QCoreApplication.translate("Dialog_settings", u"Yes", None))

        self.label_Plot_Reflectance_Title.setText(QCoreApplication.translate("Dialog_settings", u"Title", None))
        self.label_Plot_Reflectance_Insert_Legend.setText(QCoreApplication.translate("Dialog_settings", u"Insert Legend", None))
        self.comboBox_Plot_Reflectance_Insert_Legend.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Yes", None))
        self.comboBox_Plot_Reflectance_Insert_Legend.setItemText(1, QCoreApplication.translate("Dialog_settings", u"No", None))

        self.label_Plot_CIExy_Width.setText(QCoreApplication.translate("Dialog_settings", u"Width (px)", None))
        self.label_Plot_CIExy_Height.setText(QCoreApplication.translate("Dialog_settings", u"Height (px)", None))
        self.label_Plot_CIExy_Insert_Title.setText(QCoreApplication.translate("Dialog_settings", u"Insert Title", None))
        self.comboBox_Plot_CIExy_Insert_Title.setItemText(0, QCoreApplication.translate("Dialog_settings", u"No", None))
        self.comboBox_Plot_CIExy_Insert_Title.setItemText(1, QCoreApplication.translate("Dialog_settings", u"Yes", None))

        self.label_Plot_CIExy_Title.setText(QCoreApplication.translate("Dialog_settings", u"Title", None))
        self.label_Plot_CIExy_Insert_Legend.setText(QCoreApplication.translate("Dialog_settings", u"Insert Legend", None))
        self.comboBox_Plot_CIExy_Insert_Legend.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Yes", None))
        self.comboBox_Plot_CIExy_Insert_Legend.setItemText(1, QCoreApplication.translate("Dialog_settings", u"No", None))

        self.tabWidget_Settings.setTabText(self.tabWidget_Settings.indexOf(self.Plot_Settings), QCoreApplication.translate("Dialog_settings", u"Plot", None))
        self.label_Export_Separator.setText(QCoreApplication.translate("Dialog_settings", u"Export Number Separator", None))
        self.comboBox_Export_Separator.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Comma", None))
        self.comboBox_Export_Separator.setItemText(1, QCoreApplication.translate("Dialog_settings", u"Point", None))

        self.label_Copy_Header.setText(QCoreApplication.translate("Dialog_settings", u"Copy Header to Clipboard", None))
        self.comboBox_Copy_Header.setItemText(0, QCoreApplication.translate("Dialog_settings", u"Yes", None))
        self.comboBox_Copy_Header.setItemText(1, QCoreApplication.translate("Dialog_settings", u"No", None))

        self.tabWidget_Settings.setTabText(self.tabWidget_Settings.indexOf(self.Export_Settings), QCoreApplication.translate("Dialog_settings", u"Export", None))
    # retranslateUi

