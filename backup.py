import sys

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setGeometry(QtCore.QRect(360, 70, 381, 291))
        self.image.setText("")
        self.image.setObjectName("image")
        self.button_right = QtWidgets.QPushButton(self.centralwidget)
        self.button_right.setGeometry(QtCore.QRect(430, 450, 150, 50))
        self.button_right.setObjectName("button_right")
        self.button_left = QtWidgets.QPushButton(self.centralwidget)
        self.button_left.setGeometry(QtCore.QRect(130, 450, 150, 50))
        self.button_left.setObjectName("button_left")
        self.button_red = QtWidgets.QPushButton(self.centralwidget)
        self.button_red.setGeometry(QtCore.QRect(60, 120, 100, 40))
        self.button_red.setObjectName("button_red")
        self.button_green = QtWidgets.QPushButton(self.centralwidget)
        self.button_green.setGeometry(QtCore.QRect(60, 170, 100, 40))
        self.button_green.setObjectName("button_green")
        self.button_blue = QtWidgets.QPushButton(self.centralwidget)
        self.button_blue.setGeometry(QtCore.QRect(60, 220, 100, 40))
        self.button_blue.setObjectName("button_blue")
        self.button_all = QtWidgets.QPushButton(self.centralwidget)
        self.button_all.setGeometry(QtCore.QRect(60, 270, 100, 40))
        self.button_all.setObjectName("button_all")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_right.setText(_translate("MainWindow", "По часовой стрелке"))
        self.button_left.setText(_translate("MainWindow", "Против часовой стрелки"))
        self.button_red.setText(_translate("MainWindow", "R"))
        self.button_green.setText(_translate("MainWindow", "G"))
        self.button_blue.setText(_translate("MainWindow", "B"))
        self.button_all.setText(_translate("MainWindow", "ALL"))


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # uic.loadUi('main.ui', self)
        self.deg = 0
        self.f = QFileDialog.getOpenFileName(self, 'Выберите картинку', '')[0]
        self.img_orig = Image.open(self.f)
        self.img = Image.open(self.f)
        self.img1 = ImageQt(self.img)
        self.px = QPixmap.fromImage(self.img1)
        self.image.setPixmap(self.px)
        self.button_red.clicked.connect(self.channel)
        self.button_blue.clicked.connect(self.channel)
        self.button_all.clicked.connect(self.channel)
        self.button_green.clicked.connect(self.channel)
        self.button_left.clicked.connect(self.rotate)
        self.button_right.clicked.connect(self.rotate)

    def rotate(self):
        deg = -90 if self.sender() == self.button_right else 90
        if self.sender() == self.button_right:
            self.deg -= 90
        else:
            self.deg += 90
        self.deg %= 360
        self.img = self.img.rotate(deg)
        self.img1 = ImageQt(self.img)
        self.px = QPixmap.fromImage(self.img1)
        self.image.setPixmap(self.px)

    def channel(self):
        self.img = self.img_orig.copy()
        px = self.img.load()
        x, y = self.img.size
        for i in range(x):
            for j in range(y):
                r, g, b = px[i, j]
                if self.sender().text() == 'R':
                    px[i, j] = r, 0, 0
                elif self.sender().text() == 'G':
                    px[i, j] = 0, g, 0
                elif self.sender().text() == 'B':
                    px[i, j] = 0, 0, b
                else:
                    pass
        self.img = self.img.rotate(self.deg)
        self.img1 = ImageQt(self.img)
        self.px = QPixmap.fromImage(self.img1)
        self.image.setPixmap(self.px)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
