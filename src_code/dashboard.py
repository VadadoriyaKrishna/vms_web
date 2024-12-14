from PyQt5 import QtGui, QtCore, QtWidgets
from win32api import GetSystemMetrics
from collections import Counter
import xml.etree.ElementTree as ET
from  src_code.global_widgets import QHLine

class DashBoard(QtWidgets.QWidget):    
    def __init__(self, cam1, cam2, cam3, cam4, cam5, cam6, stacked_widget, parent=None):
        super(DashBoard, self).__init__(parent)

        

        # self.showMaximized()

        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(0)

        self.screen_width = int(0.7*sizeObject.width())
        self.screen_height = int(0.7*sizeObject.height())
        # self.screen_width = self.width()
        # self.screen_height = self.height() 

        self.cam1 = cam1
        self.cam2 = cam2
        self.cam3 = cam3
        self.cam4 = cam4
        self.cam5 = cam5
        self.cam6 = cam6

        self.stacked_widget = stacked_widget

        # Layouts and frames
        layout = QtWidgets.QVBoxLayout()

        top_frame = QtWidgets.QFrame()
        top_frame.setStyleSheet("background-color: rgb(89,112,117)")
        mid_frame = QtWidgets.QFrame()   
        mid_frame.setStyleSheet("background-color: rgb(11,66,61)")
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

        label = QtWidgets.QLabel(all_configuration[4])
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
        self.mid_layout = QtWidgets.QStackedLayout()

        # Create camera widgets
        print('Creating Camera Widgets...')

        cam_widget = Cam6(self.cam1, self.cam2, self.cam3, self.cam4, self.cam5, self.cam6, self.screen_width, self.screen_height, self)
        self.mid_layout.addWidget(cam_widget)
        self.mid_layout.setCurrentWidget(cam_widget)
        mid_frame.setLayout(self.mid_layout)  
        
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
        bar_label_1 = QtWidgets.QLabel('|')
        bar_label_1.setFont(QtGui.QFont('Calibri (Body)', 10))
        live_cams = QtWidgets.QLabel('Live cameras:')
        live_cams.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.live_cams = QtWidgets.QLabel('')
        self.live_cams.setFont(QtGui.QFont('Calibri (Body)', 10))
        copyright_label = QtWidgets.QLabel('@RRR Version')
        copyright_label.setFont(QtGui.QFont('Calibri (Body)', 8))

        # Toolbutton for Bounding box
        toolbutton_bb = QtWidgets.QToolButton()
        toolbutton_bb.setText('Blobs')
        toolbutton_bb.setStyleSheet("background-color: rgb(7,240,158);")
        toolbutton_bb.setStyle(QtWidgets.QStyleFactory.create("plastique"))
        toolmenu_bb = QtWidgets.QMenu()
        toolmenu_bb.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))

        action1_bb = toolmenu_bb.addAction("CAM 01")
        action1_bb.setCheckable(True)
        action1_bb.setChecked(True)
        action2_bb = toolmenu_bb.addAction("CAM 02")
        action2_bb.setCheckable(True)
        action2_bb.setChecked(True)
        action3_bb = toolmenu_bb.addAction("CAM 03")
        action3_bb.setCheckable(True)
        action3_bb.setChecked(True)
        action4_bb = toolmenu_bb.addAction("CAM 04")
        action4_bb.setCheckable(True)
        action4_bb.setChecked(True)
        action5_bb = toolmenu_bb.addAction("CAM 05")
        action5_bb.setCheckable(True)
        action5_bb.setChecked(True)
        action6_bb = toolmenu_bb.addAction("CAM 06")
        action6_bb.setCheckable(True)
        action6_bb.setChecked(True)

        toolbutton_bb.setMenu(toolmenu_bb)
        toolbutton_bb.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # action.triggered.connect(lambda: self.cam1.show_hide(True))
        action1_bb.triggered.connect(self.cam1.show_hide_bb)
        action2_bb.triggered.connect(self.cam2.show_hide_bb)
        action3_bb.triggered.connect(self.cam3.show_hide_bb)
        action4_bb.triggered.connect(self.cam4.show_hide_bb)
        action5_bb.triggered.connect(self.cam5.show_hide_bb)
        action6_bb.triggered.connect(self.cam6.show_hide_bb)
        toolbutton_bb.setFixedWidth(int(GetSystemMetrics(0)*0.05))

        


        # Toolbutton for zones display
        toolbutton = QtWidgets.QToolButton()
        toolbutton.setText('Zones')
        toolbutton.setStyleSheet("background-color: rgb(7,240,158);")
        toolbutton.setStyle(QtWidgets.QStyleFactory.create("plastique"))
        toolmenu = QtWidgets.QMenu()
        toolmenu.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))

        action1 = toolmenu.addAction("CAM 01")
        action1.setCheckable(True)
        action1.setChecked(True)
        action2 = toolmenu.addAction("CAM 02")
        action2.setCheckable(True)
        action2.setChecked(True)
        action3 = toolmenu.addAction("CAM 03")
        action3.setCheckable(True)
        action3.setChecked(True)
        action4 = toolmenu.addAction("CAM 04")
        action4.setCheckable(True)
        action4.setChecked(True)
        action5 = toolmenu.addAction("CAM 05")
        action5.setCheckable(True)
        action5.setChecked(True)
        action6 = toolmenu.addAction("CAM 06")
        action6.setCheckable(True)
        action6.setChecked(True)

        toolbutton.setMenu(toolmenu)
        toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        action1.triggered.connect(self.cam1.show_hide)
        action2.triggered.connect(self.cam2.show_hide)
        action3.triggered.connect(self.cam3.show_hide)
        action4.triggered.connect(self.cam4.show_hide)
        action5.triggered.connect(self.cam5.show_hide)
        action6.triggered.connect(self.cam6.show_hide)
        toolbutton.setFixedWidth(int(GetSystemMetrics(0)*0.05))

#---------------------------------------------------------------------------------------------------------------------------------
        # comboBox = QtWidgets.QComboBox()
        # comboBox.addItems(["Select Camera", "Camera1", "Camera2", "Camera3", "Camera4", "Camera5"])


        # show = QtWidgets.QPushButton('Show')
        # show.clicked.connect(lambda: self.cam1.show_hide(True))
        # hide = QtWidgets.QPushButton('Hide')
        # hide.clicked.connect(lambda: self.cam1.show_hide(False))
#----------------------------------------------------------------------------------------------------------------------------------
        menu = QtWidgets.QToolButton()
        menu.setText('View')
        menu.setStyleSheet("background-color: rgb(7,240,158);")
        viewType = QtWidgets.QMenu()
        group = QtWidgets.QActionGroup(viewType)
        texts = ["View 1x1", "View 1x2", "View 2x2", "View 2x3"]
        for text in texts:
            action = QtWidgets.QAction(text, viewType, checkable=True, checked=text==texts[-1])
            viewType.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        group.triggered.connect(self.onTriggered)
        menu.setMenu(viewType)
        menu.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        viewType.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
        menu.setFixedWidth(int(GetSystemMetrics(0)*0.05))

        btm_layout = QtWidgets.QHBoxLayout()
        btm_layout.addWidget(date_label)
        btm_layout.addWidget(self.date_label_1)
        btm_layout.addWidget(bar_label)
        btm_layout.addWidget(time_label)
        btm_layout.addWidget(self.time_label_1)
        btm_layout.addWidget(bar_label_1)
        btm_layout.addWidget(live_cams)
        btm_layout.addWidget(self.live_cams)
        btm_layout.addStretch(4)
        btm_layout.addWidget(copyright_label)
        btm_layout.addStretch(5)
        btm_layout.addWidget(toolbutton_bb)
        btm_layout.addWidget(toolbutton)
        btm_layout.addWidget(menu)
        # self.btm_layout.addWidget(comboBox)
        btm_layout.setContentsMargins(5,5,5,5)
        btm_frame.setLayout(btm_layout)

        # self.current_process = psutil.Process()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayDateTime)
        self.timer.start()

        self.live_cam_counter = QtCore.QTimer()
        self.live_cam_counter.setInterval(10000)
        self.live_cam_counter.timeout.connect(self.countLiveCams)
        self.live_cam_counter.start()

    def displayDateTime(self):
        self.date_label_1.setText(QtCore.QDate.currentDate().toString("dd/MM/yyyy"))
        self.time_label_1.setText(QtCore.QTime.currentTime().toString())
        # print('cpu: ',self.current_process.cpu_times())
        # print(self.current_process.cpu_percent())

    def countLiveCams(self):

        print(self.cam1.server_online, self.cam2.server_online, self.cam3.server_online,
                self.cam4.server_online, self.cam5.server_online, self.cam6.server_online)

        live_cams = {"cam1": self.cam1.server_online,
                     "cam2": self.cam2.server_online,
                     "cam3": self.cam3.server_online,
                     "cam4": self.cam4.server_online,
                     "cam5": self.cam5.server_online,
                     "cam6": self.cam6.server_online}

        print(live_cams)

        res = Counter(live_cams.values())

        if res[True] == 0:
            self.live_cams.setText(str(res[True]))
            self.live_cams.setStyleSheet("color: red;")
        else:
            self.live_cams.setText(str(res[True]))
            self.live_cams.setStyleSheet("color: green;")

    def event(self, e):
        if e.type() in (QtCore.QEvent.Show, QtCore.QEvent.Resize):
            print("dashboard ", self.screen_width, self.screen_height)
            
        return QtWidgets.QWidget.event(self, e)

    def onTriggered(self, action):
        if action.text() == 'View 1x1':
            cam1_widget = Cam1(self.cam1, self.screen_width, self.screen_height, self)
            self.mid_layout.addWidget(cam1_widget)
            self.mid_layout.setCurrentWidget(cam1_widget)

        if action.text() == 'View 1x2':
            cam2_widget = Cam2(self.cam1, self.cam2, self.screen_width, self.screen_height, self)
            self.mid_layout.addWidget(cam2_widget)
            self.mid_layout.setCurrentWidget(cam2_widget)

        if action.text() == 'View 2x2':
            cam4_widget = Cam4(self.cam1, self.cam2, self.cam3, self.cam4, self.screen_width, self.screen_height, self)
            self.mid_layout.addWidget(cam4_widget)
            self.mid_layout.setCurrentWidget(cam4_widget)

        if action.text() == 'View 2x3':
            cam6_widget = Cam6(self.cam1, self.cam2, self.cam3, self.cam4, self.cam5, self.cam6, self.screen_width, self.screen_height, self)
            self.mid_layout.addWidget(cam6_widget)
            self.mid_layout.setCurrentWidget(cam6_widget)


class Cam1(QtWidgets.QWidget):
    def __init__(self, cam1, screen_width, screen_height, parent=None):
        super(Cam1, self).__init__(parent)

        cam1.set_frame_params(screen_width, screen_height, 'CAM 01', 1)

        # Add widgets to layout
        print('Adding widgets to layout...')
        layout = QtWidgets.QGridLayout()
        layout.addWidget(cam1.get_video_display_frame(),0,0,1,1)
        layout.setContentsMargins(5,5,5,5)
        self.setLayout(layout)


class Cam2(QtWidgets.QWidget):
    def __init__(self, cam1, cam2, screen_width, screen_height, parent=None):
        super(Cam2, self).__init__(parent)

        cam1.set_frame_params(screen_width//2, screen_height, 'CAM 01', 1)
        cam2.set_frame_params(screen_width//2, screen_height, 'CAM 02', 2)

        # Add widgets to layout
        print('Adding widgets to layout...')
        layout = QtWidgets.QGridLayout()
        layout.addWidget(cam1.get_video_display_frame(),0,0,1,1)
        layout.addWidget(cam2.get_video_display_frame(),0,1,1,1)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(3)
        self.setLayout(layout)


class Cam4(QtWidgets.QWidget):
    def __init__(self, cam1, cam2, cam3, cam4, screen_width, screen_height, parent=None):
        super(Cam4, self).__init__(parent)

        cam1.set_frame_params(screen_width//2, screen_height//2, 'CAM 01', 1)
        cam2.set_frame_params(screen_width//2, screen_height//2, 'CAM 02', 2)
        cam3.set_frame_params(screen_width//2, screen_height//2, 'CAM 03', 3)
        cam4.set_frame_params(screen_width//2, screen_height//2, 'CAM 04', 4)

        # Add widgets to layout
        print('Adding widgets to layout...')
        layout = QtWidgets.QGridLayout()
        layout.addWidget(cam1.get_video_display_frame(),0,0,1,1)
        layout.addWidget(cam2.get_video_display_frame(),0,1,1,1)
        layout.addWidget(cam3.get_video_display_frame(),1,0,1,1)
        layout.addWidget(cam4.get_video_display_frame(),1,1,1,1)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(3)
        self.setLayout(layout)


class Cam6(QtWidgets.QWidget):
    def __init__(self, cam1, cam2, cam3, cam4, cam5, cam6, screen_width, screen_height, parent=None):
        super(Cam6, self).__init__(parent)

        cam1.set_frame_params(screen_width//3, screen_height//2, 'CAM 01', 1)                                  
        cam2.set_frame_params(screen_width//3, screen_height//2, 'CAM 02', 2)
        cam3.set_frame_params(screen_width//3, screen_height//2, 'CAM 03', 3)
        cam4.set_frame_params(screen_width//3, screen_height//2, 'CAM 04', 4)
        cam5.set_frame_params(screen_width//3, screen_height//2, 'CAM 05', 5)
        cam6.set_frame_params(screen_width//3, screen_height//2, 'CAM 06', 6)

        # Add widgets to layout
        print('Adding widgets to layout...')
        layout = QtWidgets.QGridLayout()
        layout.addWidget(cam1.get_video_display_frame(),0,0,1,1)
        layout.addWidget(cam2.get_video_display_frame(),0,1,1,1)
        layout.addWidget(cam3.get_video_display_frame(),0,2,1,1)
        layout.addWidget(cam4.get_video_display_frame(),1,0,1,1)
        layout.addWidget(cam5.get_video_display_frame(),1,1,1,1)
        layout.addWidget(cam6.get_video_display_frame(),1,2,1,1)
        # layout.setHorizontalSpacing(3)
        # layout.setVerticalSpacing(3)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(3)
        self.setLayout(layout)




# All configurations
tree = ET.parse('Configurations/all_configurations.xml')
root = tree.getroot()
all_configuration = []
for elem in root:
    for subelem in elem:
        all_configuration.append(subelem.text)