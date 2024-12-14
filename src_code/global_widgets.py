from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QObject, QSize, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot, Qt
from PyQt5.QtGui import QPainter, QPalette, QLinearGradient, QGradient, QColor 
from PyQt5.QtWidgets import QAbstractButton, QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout


cameras = None


class QHLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(QHLine, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setStyleSheet("background-color: rgb(208, 208, 225);")


class SwitchPrivate(QObject):
    def __init__(self, q, parent=None):
        QObject.__init__(self, parent=parent)
        self.mPointer = q
        self.mPosition = 0.0
        self.mGradient = QLinearGradient()
        self.mGradient.setSpread(QGradient.PadSpread)

        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b'position')
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutExpo)

        self.animation.finished.connect(self.mPointer.update)

    @pyqtProperty(float)
    def position(self):
        return self.mPosition

    @position.setter
    def position(self, value):
        self.mPosition = value
        self.mPointer.update()

    def draw(self, painter):
        r = self.mPointer.rect()
        margin = r.height()/10
        shadow = self.mPointer.palette().color(QPalette.Dark)
        light = self.mPointer.palette().color(QPalette.Light)
        button = self.mPointer.palette().color(QPalette.Button)
        painter.setPen(Qt.NoPen)

        if self.mPointer.isChecked():
            self.mGradient.setColorAt(0, QColor(0, 128, 255))
            self.mGradient.setColorAt(1, QColor(0, 128, 255))
        else:
            self.mGradient.setColorAt(0, shadow.darker(140))
            self.mGradient.setColorAt(1, light.darker(160))
        self.mGradient.setStart(0, r.height())
        self.mGradient.setFinalStop(0, 0)
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r, r.height()/2, r.height()/2)

        # self.mGradient.setColorAt(0, QColor(0, 128, 255))
        # self.mGradient.setColorAt(1, QColor(0, 128, 255))
        # self.mGradient.setStart(0, 0)
        # self.mGradient.setFinalStop(0, r.height())
        # painter.setBrush(self.mGradient)
        # painter.drawRoundedRect(r.adjusted(margin, margin, -margin, -margin), r.height()/2, r.height()/2)

        self.mGradient.setColorAt(0, button.lighter(130))
        self.mGradient.setColorAt(1, button)

        painter.setBrush(self.mGradient)

        x = r.height()/2.0 + self.mPosition*(r.width()-r.height())
        painter.drawEllipse(QPointF(x, r.height()/2), r.height()/2-margin, r.height()/2-margin)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked):
        self.animation.setDirection(QPropertyAnimation.Forward if checked else QPropertyAnimation.Backward)
        self.animation.start()

    def __del__(self):
        del self.animation


class Switch(QAbstractButton):
    def __init__(self, parent=None):
        QAbstractButton.__init__(self, parent=parent)
        self.dPtr = SwitchPrivate(self)
        self.setCheckable(True)
        self.clicked.connect(self.dPtr.animate)

    def sizeHint(self):
        return QSize(42, 21)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.dPtr.draw(painter)

    def resizeEvent(self, event):
        self.update()

    def __del__(self):
        del self.dPtr


# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
        
#         layout = QVBoxLayout()

#         self.status = False

#         self.switch = Switch()
#         self.switch.setChecked(False)
#         self.switch.clicked.connect(self.state)
#         layout.addWidget(self.switch)
#         self.setLayout(layout)

#     def state(self):
#         if self.status == True:
#             self.status = False
#             print(self.status)
#         else:
#             self.status = True
#             print(self.status)


# if __name__ == '__main__':
#     import sys
#     app = QApplication([])
#     w = Window()
#     w.show()
#     sys.exit(app.exec_())