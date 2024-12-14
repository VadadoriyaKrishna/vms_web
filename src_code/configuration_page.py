from PyQt5 import QtGui, QtCore, QtWidgets
from win32api import GetSystemMetrics
import xml.etree.ElementTree as ET
from . import global_widgets as gw
from .global_widgets import Switch, QHLine


class ZoneConfig(QtWidgets.QWidget):
    def __init__(self, cam=None, stacked_widget=None, idx=None, parent=None):
        super(ZoneConfig, self).__init__(parent)

        self.cam = cam
        self.stacked_widget = stacked_widget
        self.idx = idx        

        # Layouts and frames
        layout = QtWidgets.QVBoxLayout()

        top_frame = QtWidgets.QFrame()
        top_frame.setStyleSheet("background-color: rgb(89,112,117)")
        mid_frame = QtWidgets.QFrame()   
        # mid_frame.setStyleSheet("background-color: rgb(153, 187, 255)")
        btm_frame = QtWidgets.QFrame()
        btm_frame.setStyleSheet("background-color: rgb(89,112,117)")

        layout.addWidget(top_frame, 1)
        layout.addWidget(QHLine())
        layout.addWidget(mid_frame, 20)
        layout.addWidget(QHLine())
        layout.addWidget(btm_frame, 1)
 
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Top frame
        vendor_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap('Images/logo_logo.jpg')
        vendor_logo.setPixmap(pixmap)

        label = QtWidgets.QLabel('VIDEO Configuration')
        label.setFont(QtGui.QFont('Engravers MT', 20))

        client_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(all_configuration[3])
        client_logo.setPixmap(pixmap)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(vendor_logo, alignment=QtCore.Qt.AlignLeft)
        top_layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)
        top_layout.addWidget(client_logo, alignment=QtCore.Qt.AlignRight)
        top_layout.setContentsMargins(5,5,5,5)
        top_frame.setLayout(top_layout)

        # Middle frame
        mid_layout = QtWidgets.QHBoxLayout()

        # Middle frame left
        mid_frame_left = QtWidgets.QFrame()
        mid_layout_left = QtWidgets.QVBoxLayout()
        mid_layout_left.setContentsMargins(0,0,0,0)
        mid_layout_left.setSpacing(0)
        
        # Middle frame left top
        mid_frame_left_top = QtWidgets.QFrame()
        mid_frame_left_top.setStyleSheet("background-color: rgb(145,184,199)")
        mid_layout_left_top = QtWidgets.QVBoxLayout()

        heading1 = QtWidgets.QLabel('INFORMATIONS')
        heading1.setFont(QtGui.QFont('Engravers MT', 15))
        heading1.setStyleSheet("border-bottom-width: 1px; border-bottom-style: solid; border-radius: 0px;")

        # self.mid_layout_left_top.addWidget(self.obj, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_top.addWidget(heading1, alignment=QtCore.Qt.AlignCenter)
        # self.mid_layout_left_top.addWidget(self.fields)
        mid_layout_left_top.setContentsMargins(0,10,0,0)
        mid_layout_left_top.setSpacing(0)
        mid_frame_left_top.setLayout(mid_layout_left_top)
        mid_layout_left.addWidget(mid_frame_left_top, 1)

        # Middle frame left mid
        mid_frame_left_mid = QtWidgets.QFrame()
        mid_frame_left_mid.setStyleSheet("background-color: rgb(183,198,201)")
        mid_layout_left_mid = QtWidgets.QVBoxLayout()

        mid_frame_left_mid_inner = QtWidgets.QFrame()
        mid_frame_left_mid_inner.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # mid_frame_left_mid_inner.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        mid_frame_left_mid_inner.setStyleSheet("background-color: rgb(183,198,201);")
        mid_layout_left_mid_inner = QtWidgets.QVBoxLayout()
        mid_layout_left_mid.addWidget(mid_frame_left_mid_inner)
        mid_layout_left_mid.setContentsMargins(8,0,8,8)

        self.fields = DynamicFields(self.cam)

        mid_layout_left_mid_inner.addWidget(self.fields)
        mid_frame_left_mid_inner.setLayout(mid_layout_left_mid_inner)
        # mid_layout_left_mid.addWidget(self.fields)
        mid_frame_left_mid.setLayout(mid_layout_left_mid)

        mid_layout_left.addWidget(mid_frame_left_mid, 6)
        mid_layout_left.addWidget(QHLine())

        # Middle frame left bottom
        mid_frame_left_btm = QtWidgets.QFrame()
        mid_frame_left_btm.setStyleSheet("background-color: rgb(167,141,201)")
        mid_layout_left_btm = QtWidgets.QVBoxLayout()

        heading_2 = QtWidgets.QLabel('VMS Manager')
        heading_2.setFont(QtGui.QFont('Engravers MT', 15))
        heading_2.setStyleSheet("border-bottom-width: 1px; border-bottom-style: solid; border-radius: 0px;")

        self.toggle_btn = Switch()
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.state)

        self.btn_1 = QtWidgets.QPushButton('Func 01')
        self.btn_1.clicked.connect(self.cam.zone_manager.confirm)
        self.btn_2 = QtWidgets.QPushButton('Func 02')
        self.btn_2.clicked.connect(self.cam.zone_manager.reset)
        self.btn_3 = QtWidgets.QPushButton('Save Func')
        self.btn_3.clicked.connect(self.cam.zone_manager.save)
        # self.btn_4 = QtWidgets.QPushButton('Load Zones')
        # self.btn_4.clicked.connect(self.cam.zone_manager.load)
        self.btn_5 = QtWidgets.QPushButton('Delete Func')
        self.btn_5.clicked.connect(self.delete_zones)
       
        mid_layout_left_btm.addWidget(heading_2, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_btm.addWidget(self.toggle_btn, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_btm.addWidget(self.btn_1, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_btm.addWidget(self.btn_2, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_btm.addWidget(self.btn_3, alignment=QtCore.Qt.AlignCenter)
        # mid_layout_left_btm.addWidget(self.btn_4, alignment=QtCore.Qt.AlignCenter)
        mid_layout_left_btm.addWidget(self.btn_5, alignment=QtCore.Qt.AlignCenter)
        mid_frame_left_btm.setLayout(mid_layout_left_btm)

        mid_layout_left.addWidget(mid_frame_left_btm, 4)

        mid_frame_left.setLayout(mid_layout_left)

        # Middle frame right
        self.mid_frame_right = QtWidgets.QFrame()
        self.mid_frame_right.setStyleSheet("background-color: rgb(0, 187, 255)")

        # Create camera widgets
        print('Creating Camera Widgets...')
        mid_layout_right = QtWidgets.QHBoxLayout()
        self.video_frame = self.cam.get_video_frame()
        mid_layout_right.addWidget(self.video_frame)
        mid_layout_right.setContentsMargins(5,5,5,5)
        self.mid_frame_right.setLayout(mid_layout_right)

        # Mouse click event
        self.video_frame.mousePressEvent = self.cam.getPos

        mid_layout.addWidget(mid_frame_left, 25)
        mid_layout.addWidget(self.mid_frame_right, 75)
        mid_layout.setContentsMargins(0,0,0,0)
        mid_layout.setSpacing(0)
        mid_frame.setLayout(mid_layout)   

        # Bottom frame
        date_label = QtWidgets.QLabel('Date:')
        date_label.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.date_label_1 = QtWidgets.QLabel('')
        self.date_label_1.setFont(QtGui.QFont('Calibri (Body)', 10))
        bar_label = QtWidgets.QLabel('|')
        bar_label.setFont(QtGui.QFont('Calibri (Body)', 10))
        time_label = QtWidgets.QLabel('Time:')
        time_label.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.time_label_1 = QtWidgets.QLabel('')
        self.time_label_1.setFont(QtGui.QFont('Calibri (Body)', 10))
        copyright_label = QtWidgets.QLabel('VMS@version2022')
        copyright_label.setFont(QtGui.QFont('Calibri (Body)', 8))
        btn = QtWidgets.QPushButton('Dashboard')
        btn.setFixedWidth(int(GetSystemMetrics(0)*0.07))
        btn.setStyleSheet("background-color: rgb(184,245,239); border-color: rgb(115, 115, 115); border-style: solid; border-width: 1px; padding: 4px; border-radius: 2px;")
        # btn.setStyleSheet("background-color: orange; border-style: outset; border-width: 1px; border-radius: 15px; border-color: black; padding: 4px;")
        btn.clicked.connect(self.goMainWindow)

#------------------------------------------------------------------------------------------------------------------------------
        # This is unique for every window, therefore checkable is causing problem. Can be fixed if mid_layout is QStackedLayout
        menu = QtWidgets.QToolButton()
        menu.setText('Select Camera')
        menu.setStyleSheet("background-color: rgb(184,245,239); padding: 1px;")
        viewType = QtWidgets.QMenu()
        group = QtWidgets.QActionGroup(viewType)
        texts = ["Video 01", "Video 02", "Video 03", "Video 04", "Video 05", "Video 06"]
        for text in texts:
            # action = QtWidgets.QAction(text, viewType, checkable=True, checked=text==texts[self.idx-1])
            action = QtWidgets.QAction(text, viewType)
            viewType.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        group.triggered.connect(self.onTriggered)
        menu.setMenu(viewType)
        menu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        viewType.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
        menu.setFixedWidth(int(GetSystemMetrics(0)*0.07))
#------------------------------------------------------------------------------------------------------------------------------

        btm_layout = QtWidgets.QHBoxLayout()
        btm_layout.addWidget(date_label)
        btm_layout.addWidget(self.date_label_1)
        btm_layout.addWidget(bar_label)
        btm_layout.addWidget(time_label)
        btm_layout.addWidget(self.time_label_1)
        btm_layout.addStretch()
        btm_layout.addWidget(copyright_label)
        btm_layout.addStretch()
        btm_layout.addWidget(menu)
        btm_layout.addWidget(btn)
        btm_layout.setContentsMargins(5,5,5,5)
        btm_frame.setLayout(btm_layout)

        self.setLayout(layout)
        # self.showMaximized()

        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(0)

        self.screen_width = int(0.7*sizeObject.width())
        self.screen_height = int(0.7*sizeObject.height())
        # self.screen_width = self.width()
        # self.screen_height = self.height()

        # self.btn_1.setFixedWidth(int(self.screen_width*0.07))
        # self.btn_2.setFixedWidth(int(self.screen_width*0.07))
        # self.btn_3.setFixedWidth(int(self.screen_width*0.07))
        # self.btn_4.setFixedWidth(int(self.screen_width*0.07))
        # self.btn_5.setFixedWidth(int(self.screen_width*0.07))

        self.btn_list = [self.btn_1, self.btn_2, self.btn_3, self.btn_5]
        for x in self.btn_list:
            x.setFixedWidth(int(GetSystemMetrics(0)*0.07))
            x.setStyleSheet("background-color: rgb(184,245,239);")
            x.setEnabled(False)

        self.cam.set_frame_params_1(self.mid_frame_right.width(), self.mid_frame_right.height()-10)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayDateTime)
        self.timer.start()

    def displayDateTime(self):
        self.date_label_1.setText(QtCore.QDate.currentDate().toString("dd/MM/yyyy"))
        self.time_label_1.setText(QtCore.QTime.currentTime().toString())

    def event(self, e):
        if e.type() in (QtCore.QEvent.Show, QtCore.QEvent.Resize):
            self.cam.set_frame_params_1(self.mid_frame_right.width()-10, self.mid_frame_right.height()-10)
            print('conf: ', self.mid_frame_right.width()-10, self.mid_frame_right.height()-10)

        return QtWidgets.QWidget.event(self, e)

    def state(self):
        if self.cam.zone_manager.draw_zones == True:
            self.cam.zone_manager.draw_zones = False
            for x in self.btn_list:
                x.setEnabled(False)
        else:
            self.cam.zone_manager.draw_zones = True
            for x in self.btn_list:
                x.setEnabled(True)

    def onTriggered(self, action):
        # global cameras

        for cam in gw.cameras:
            cam.show_zones = False
            cam.show_bounding_box = False

        if self.cam.zone_manager.unsaved_changes == False:
            if action.text() == 'Video 01':
                self.stacked_widget.setCurrentIndex(1)
            elif action.text() == 'Video 02':
                self.stacked_widget.setCurrentIndex(2)
            elif action.text() == 'Video 03':
                self.stacked_widget.setCurrentIndex(3)
            elif action.text() == 'Video 04':
                self.stacked_widget.setCurrentIndex(4)
            elif action.text() == 'Video 05':
                self.stacked_widget.setCurrentIndex(5)
            elif action.text() == 'Video 06':
                self.stacked_widget.setCurrentIndex(6)
        else:
            mbox = QtWidgets.QMessageBox.question(self,"Warning!","You have some unsaved changes.\nDo you want to proceed anyway?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
            if mbox == QtWidgets.QMessageBox.Yes:
                self.cam.zone_manager.reset()
                self.cam.zone_manager.load()
                if action.text() == 'Video 01':
                    self.stacked_widget.setCurrentIndex(1)
                elif action.text() == 'Video 02':
                    self.stacked_widget.setCurrentIndex(2)
                elif action.text() == 'Video 03':
                    self.stacked_widget.setCurrentIndex(3)
                elif action.text() == 'Video 04':
                    self.stacked_widget.setCurrentIndex(4)
                elif action.text() == 'Video 05':
                    self.stacked_widget.setCurrentIndex(5)
                elif action.text() == 'Video 06':
                    self.stacked_widget.setCurrentIndex(6)

    def delete_zones(self):
        mbox = QtWidgets.QMessageBox.question(self,"Warning!","Are you sure you want to delete all zones?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
        if mbox == QtWidgets.QMessageBox.Yes:
            self.cam.zone_manager.delete()
        # elif mbox==QMessageBox.No:
            # print("You Clicked No Button")

    def goMainWindow(self):
        # self.cam.show_zones = self.cam.pre_zone_state
        # self.cam.show_bounding_box = self.cam.pre_box_state
        # global cameras

        for cam in gw.cameras:
            cam.show_zones = cam.pre_zone_state
            cam.show_bounding_box = cam.pre_box_state

        if self.cam.zone_manager.unsaved_changes == False:
            self.stacked_widget.setCurrentIndex(0)
        else:
            # QtWidgets.QMessageBox.warning(
            #     self, 'Error', 'You have some unsaved changes')
            mbox = QtWidgets.QMessageBox.question(self,"Warning!","You have some unsaved changes.\nDo you want to proceed anyway?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
            if mbox == QtWidgets.QMessageBox.Yes:
                self.cam.zone_manager.reset()
                self.cam.zone_manager.load()
                self.stacked_widget.setCurrentIndex(0)


class DynamicFields(QtWidgets.QWidget):
    def __init__(self, cam=None, parent=None):
        super(DynamicFields, self).__init__(parent)

        self.cam = cam

        layout = QtWidgets.QGridLayout()

        name = QtWidgets.QLabel('Camera:')
        # name.setStyleSheet("color: black; font-family: Engravers MT; font-size: 18px; font-weight: bold;")
        name.setStyleSheet("color: black; font-weight: bold;")
        name.setFont(QtGui.QFont('Engravers MT', 12))
        label1 = QtWidgets.QLabel('Camera status:')
        label1.setFont(QtGui.QFont('Calibri (Body)', 10))
        # label1.setFont(QtGui.QFont('Calibri (Body)', 10, weight=QtGui.QFont.Bold))
        label2 = QtWidgets.QLabel('Info 01:')
        label2.setFont(QtGui.QFont('Calibri (Body)', 10))
        label3 = QtWidgets.QLabel('Info 02:')
        label3.setFont(QtGui.QFont('Calibri (Body)', 10))
        # label4 = QtWidgets.QLabel('Average speed:')
        # label4.setFont(QtGui.QFont('Calibri (Body)', 10))
        label5 = QtWidgets.QLabel('Info 03:')
        label5.setFont(QtGui.QFont('Calibri (Body)', 10))

        if self.cam.idx <= 9:
            self.cam_name = QtWidgets.QLabel('Video 0'+str(self.cam.idx))
        else:
            self.cam_name = QtWidgets.QLabel('Video '+str(self.cam.idx))
        # self.cam_name.setStyleSheet("color: black; font-family: Engravers MT; font-size: 18px; font-weight: bold;")
        self.cam_name.setStyleSheet("color: black; font-weight: bold;")
        self.cam_name.setFont(QtGui.QFont('Engravers MT', 12))
        # self.value1 = QtWidgets.QLabel('')
        # self.value1.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.value1 = QtWidgets.QLabel('')
        self.value2 = QtWidgets.QLabel('')
        self.value2.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.value3 = QtWidgets.QLabel('')
        self.value3.setFont(QtGui.QFont('Calibri (Body)', 10))
        # self.value4 = QtWidgets.QLabel('')
        # self.value4.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.value5 = QtWidgets.QLabel('')
        self.value5.setFont(QtGui.QFont('Calibri (Body)', 10))

        layout.addWidget(name, 0,0,1,1, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(label1, 1,0,1,1, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(label2, 2,0,1,1, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(label3, 3,0,1,1, alignment=QtCore.Qt.AlignCenter)
        # layout.addWidget(label4, 4,0,1,1, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(label5, 5,0,1,1, alignment=QtCore.Qt.AlignCenter)

        layout.addWidget(self.cam_name, 0,1,1,1)
        layout.addWidget(self.value1, 1,1,1,1)
        layout.addWidget(self.value2, 2,1,1,1)
        layout.addWidget(self.value3, 3,1,1,1)
        # layout.addWidget(self.value4, 4,1,1,1)
        layout.addWidget(self.value5, 5,1,1,1)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        # self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayValues)
        self.timer.start(1000)

    def displayValues(self):
        if self.cam is not None:
            if self.cam.server_online:
                self.value1.setText('Connected')
                self.value1.setStyleSheet("color: green;")
                self.value1.setFont(QtGui.QFont('Calibri (Body)', 10))
            else:
                self.value1.setText('Not connected')
                self.value1.setStyleSheet("color: red;")
                self.value1.setFont(QtGui.QFont('Calibri (Body)', 10))
            self.value2.setText(str(self.cam.flow_type))
            self.value3.setText(str(self.cam.zone_occupancy))
            self.value5.setText(str(self.cam.fog_status))




# All configurations
tree = ET.parse('Configurations/all_configurations.xml')
root = tree.getroot()
all_configuration = []
for elem in root:
    for subelem in elem:
        all_configuration.append(subelem.text)