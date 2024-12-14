import os
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect
from threading import Thread, RLock, Lock
from collections import deque
from datetime import datetime
from flask import Flask, render_template, Response, request, jsonify
from flask_cors import CORS, cross_origin
import time
import sys
import cv2
import imutils
import requests
import jsonpickle
import numpy as np
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
from win32api import GetSystemMetrics
lock = Lock()
import logging
import xml.etree.ElementTree as ET
from src_code.dashboard import DashBoard
from src_code.configuration_page import ZoneConfig
from src_code.zone_manager import ZoneManager
from src_code import global_widgets as gw
from src_code.trigger_no_connection_event import trigger_no_connection_event

path = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(os.getcwd())


logging.basicConfig(filename="Logs/{}".format(datetime.now().strftime('%d_%m_%Y.log')),
                    filemode='a',
                    format='%(asctime)s:%(msecs)d-%(name)s-%(levelname)s--%(message)s',
                    datefmt='%H:%M:%S',level=logging.DEBUG)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)


"""Closes duplicate instance of the application"""

class MultipleInstanceError(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MultipleInstanceError, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon('Images/logo_logo.jpg'))
        self.setWindowTitle('VIDIO')

        QtWidgets.QMessageBox.warning(
            self, 'Error', 'Application is already running!')

        logging.info("Duplicate instance of the application was launched")
        print("Already running")
        sys.exit(0)


class CameraWidget(QtWidgets.QWidget):
    """Independent camera feed
    Uses threading to grab IP camera frames in the background

    @param width - Width of the video frame
    @param height - Height of the video frame
    @param stream_link - IP/RTSP/Webcam link
    @param aspect_ratio - Whether to maintain frame aspect ratio or force into fraame
    """

    def __init__(self, stream_link=0, stacked_widget=None, width=0, height=0, btn_text=None, idx=None, aspect_ratio=False, parent=None, deque_size=20):
        super(CameraWidget, self).__init__(parent)

        # Initialize deque used to store frames read from the stream
        self.deque = deque(maxlen=deque_size)
        
        self.maintain_aspect_ratio = aspect_ratio
        self.camera_stream_link = stream_link
        self.stacked_widget = stacked_widget
        self.idx = idx

        # Flag to check if camera is valid/working
        self.online = False
        self.capture = None

        # Flag to show/hide zones on dashboard
        self.show_zones = True
        self.show_bounding_box = True
        self.pre_zone_state = self.show_zones
        self.pre_box_state = self.show_bounding_box

        self.server_online = True

        self.video_frame = QtWidgets.QLabel()
        self.video_frame_1 = QtWidgets.QLabel()

        self.load_network_stream()

        # Make an object of ZoneManager class and initialize a point
        self.zone_manager = ZoneManager( self.idx)
        self.point = (-1,-1)

        self.server_status = 'Not connected'
        self.flow_type = 'Unavailable'
        self.zone_occupancy = 'Unavailable'
        self.fog_status = 'Unavailable'

        self.last_receive_time = 0
        self.last_server_time = 0

        self.err_image = cv2.imread('Images/cam_error.jpg')
        self.err_image = cv2.cvtColor(self.err_image, cv2.COLOR_BGR2RGB)

        # Start background frame grabbing
        self.get_frame_thread = Thread(target=self.get_frame, args=())
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()

        self.check_status = QtCore.QTimer()
        # self.timer.setInterval(1000)
        self.check_status.timeout.connect(self.check_server)
        self.check_status.start(15000)

        # Periodically set video frame to display
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.set_frame)
        self.timer.start(500)

        print('Started camera: {}'.format(self.camera_stream_link))

    def show_hide_bb(self):
        if self.show_bounding_box == True:
            self.show_bounding_box = False
            self.pre_box_state = self.show_bounding_box
        else:
            self.show_bounding_box = True
            self.pre_box_state = self.show_bounding_box

    def show_hide(self):
        if self.show_zones == True:
            self.show_zones = False
            self.pre_zone_state = self.show_zones
        else:
            self.show_zones = True
            self.pre_zone_state = self.show_zones

    def load_network_stream(self):
        """Verifies stream link and open new stream if valid"""

        def load_network_stream_thread():
            if self.verify_network_stream(self.camera_stream_link):
                self.capture = cv2.VideoCapture(self.camera_stream_link)
                self.online = True
        self.load_stream_thread = Thread(target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def verify_network_stream(self, link):
        """Attempts to receive a frame from given link"""

        cap = cv2.VideoCapture(link)
        if not cap.isOpened():
            return False
        cap.release()
        return True

    def get_frame(self):
        # time.sleep(5)
        """Reads frame, resizes, and converts image to pixmap"""

        while True:
            var = 0

            if time.time() - self.last_receive_time > 5:

                # start_time = time.time()
                self.server_online = False
                # self.video_btn.setStyleSheet("background-color: rgb(255, 51, 51);")
                if var != 1:
                    self.server_status = 'Not connected'
                    self.flow_type = 'Unavailable'
                    self.zone_occupancy = 'Unavailable'
                    self.fog_status = 'Unavailable'
                    var += 1

                try:
                    if self.capture.isOpened() and self.online:
                        # Read next frame from stream and insert into deque
                        status, frame = self.capture.read()

                        if self.show_zones == True:
                            # Frame width and height should be provided to avoid offset of clicked point
                            frame = self.zone_manager.run(frame, self.screen_width_1, self.screen_height_1)

                        if status:
                            self.deque.append(frame)
                        else:
                            self.capture.release()
                            self.online = False

                        '''Triggers 'server not connected error' event'''
                        if time.time() - self.last_server_time > 300:
                            trigger_no_connection_event(self.idx)
                            self.last_server_time = time.time()

                    else:
                        # If camera is not connected, an error image is displayed to the user
                        self.deque.append(self.err_image)

                        # Attempt to reconnect
                        print('attempting to reconnect', self.camera_stream_link)
                        self.load_network_stream()
                        self.spin(2)
                    self.spin(.001)
                
                except AttributeError:
                    self.deque.append(self.err_image)

                    if self.verify_network_stream(self.camera_stream_link):
                        self.capture = cv2.VideoCapture(self.camera_stream_link)
                        self.online = True
            else:
                self.server_online = True
                var = 0
                # self.video_btn.setStyleSheet("background-color: rgb(128, 159, 255);")
                time.sleep(60)

    def spin(self, seconds):
        """Pause for set amount of seconds, replaces time.sleep so program doesnt stall"""

        time_end = time.time() + seconds
        while time.time() < time_end:
            QtWidgets.QApplication.processEvents()

    def set_frame(self):
        """Sets pixmap image to video frame"""

        if not self.online:
            try:
                frame = self.deque.popleft()
                self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = self.frame.shape
                bytesPerLine = ch * w
                self.img = QtGui.QImage(self.frame, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                self.pix = QtGui.QPixmap.fromImage(self.img)
                self.video_frame.setPixmap(self.pix)

                frame_1 = frame.copy()
                self.frame_1 = cv2.resize(frame_1, (self.screen_width_1, self.screen_height_1))
                self.frame_1 = cv2.cvtColor(self.frame_1, cv2.COLOR_BGR2RGB)
                h_1, w_1, ch_1 = self.frame_1.shape
                bytesPerLine_1 = ch_1 * w_1
                self.img_1 = QtGui.QImage(self.frame_1, w_1, h_1, bytesPerLine_1, QtGui.QImage.Format_RGB888)
                self.pix_1 = QtGui.QPixmap.fromImage(self.img_1)
                self.video_frame_1.setPixmap(self.pix_1)

                self.spin(1)
                return

            except:
                pass

        if self.deque and self.online:
            # Grab latest frame
            frame = self.deque.popleft()
            frame_1 = frame                                                                         # frame_1:  <class 'numpy.ndarray'>

            # Display frames on dashboard and configuration pages
            # Frame for dashboard
            # Keep frame aspect ratio
            if self.maintain_aspect_ratio:
                self.frame = imutils.resize(frame, width=self.screen_width)
            # Force resize
            else:
                self.frame = cv2.resize(frame, (self.screen_width, self.screen_height))

                # if self.show_bounding_box == False or self.server_online == False:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = self.frame.shape
                bytesPerLine = ch * w

            # Frame for configuration page-----------------------------------------------------------------------------------------
            if True:
                frame_1 = self.zone_manager.run(frame_1, self.screen_width_1, self.screen_height_1)

                self.frame_1 = cv2.resize(frame_1, (self.screen_width_1, self.screen_height_1))
                self.frame_1 = cv2.cvtColor(self.frame_1, cv2.COLOR_BGR2RGB)
                h_1, w_1, ch_1 = self.frame_1.shape
                bytesPerLine_1 = ch_1 * w_1

                def nested():
                    self.zone_manager.make_points2(self.point)

                nested()
                self.point = (-1,-1)

            # Convert to pixmap and set to video frame
            self.img = QtGui.QImage(self.frame, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.pix = QtGui.QPixmap.fromImage(self.img)
            self.video_frame.setPixmap(self.pix)

            self.img_1 = QtGui.QImage(self.frame_1, w_1, h_1, bytesPerLine_1, QtGui.QImage.Format_RGB888)
            self.pix_1 = QtGui.QPixmap.fromImage(self.img_1)
            self.video_frame_1.setPixmap(self.pix_1)

    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y()
        self.point = (x, y)

    def set_frame_params(self, width, height, btn_text=None, idx=0):
        self.screen_width = width
        self.screen_height = height
        self.btn_text = btn_text
        self.idx = idx

    def set_frame_params_1(self, width, height):
        self.screen_width_1 = width
        self.screen_height_1 = height

    def get_video_display_frame(self):
        self.video_display_frame = QtWidgets.QFrame()
        self.video_layout = QtWidgets.QVBoxLayout()
        self.video_btn = QtWidgets.QPushButton(self.btn_text)
        # self.video_btn.setStyleSheet("background-color: rgb(128, 159, 255);")
        if self.server_online == True:
            self.video_btn.setStyleSheet("background-color: rgb(0, 159, 0);")
        else:
            self.video_btn.setStyleSheet("background-color: rgb(0, 159, 0);")
        self.video_btn.clicked.connect(self.message)
        # self.video_frame = QtWidgets.QLabel()
        self.video_frame.setScaledContents(True)
        self.video_layout.addWidget(self.video_btn)
        self.video_layout.addWidget(self.video_frame)
        self.video_layout.setContentsMargins(0,0,0,0)
        self.video_layout.setSpacing(0)
        self.video_display_frame.setLayout(self.video_layout)

        return self.video_display_frame

    def get_video_frame(self):
        self.video_frame_1.setScaledContents(True)
        return self.video_frame_1

    def check_server(self):
        if self.server_online == True:
            self.video_btn.setStyleSheet("background-color: rgb(7,240,158);")
            # return
        else:
            self.video_btn.setStyleSheet("background-color: rgb(7,240,158);")

    def message(self):
        self.show_bounding_box = False
        self.show_zones = False
        self.stacked_widget.setCurrentIndex(self.idx)


class Username(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Username, self).__init__(parent)
        self.label = QtWidgets.QLabel('Username: ')
        self.label.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.textName = QtWidgets.QLineEdit(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.textName)
        # layout.setContentsMargins(15,0,15,0)


class Password(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Password, self).__init__(parent)
        self.label = QtWidgets.QLabel('Password: ')
        self.label.setFont(QtGui.QFont('Calibri (Body)', 10))
        self.textPass = QtWidgets.QLineEdit(self)
        self.textPass.setEchoMode(QtWidgets.QLineEdit.Password)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.textPass)
        # layout.setContentsMargins(15,0,15,0)


class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon('Images/logo_logo.jpg'))
        self.setWindowTitle('VIDEO')

        self.message = QtWidgets.QLabel("VMS")
        self.message.setFont(QtGui.QFont('Engravers MT', 16))
        # self.message_2 = QtWidgets.QLabel("Please enter username and password to proceed.")
        # self.message_2.setFont(QtGui.QFont('Engravers MT', 14))
        self.space = QtWidgets.QLabel('')
        self.username = Username()
        self.password = Password()
        self.buttonLogin = QtWidgets.QPushButton('Login', self)
        self.buttonLogin.setFixedWidth(80)
        self.buttonLogin.clicked.connect(self.handleLogin)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.message, alignment=QtCore.Qt.AlignCenter)
        # layout.addWidget(self.message_2, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.space)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.buttonLogin, alignment=QtCore.Qt.AlignCenter)

    def handleLogin(self):
        if (self.username.textName.text() == 'h' and
            self.password.textPass.text() == 'h'):
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Incorrect username or password')

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        """ This line is required so that application doesn't go out of the window
            when 'view' is changed"""
        self.setMinimumSize(150,150)

        self.setWindowTitle('VIDEO')
        self.setWindowIcon(QtGui.QIcon('Images/logo_logo.jpg'))

        self.stacked_widget = QtWidgets.QStackedWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.stacked_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.cam1 = CameraWidget(camera_ip[0], self.stacked_widget, idx=1)
        self.cam2 = CameraWidget(camera_ip[1], self.stacked_widget, idx=2)
        self.cam3 = CameraWidget(camera_ip[2], self.stacked_widget, idx=3)
        self.cam4 = CameraWidget(camera_ip[3], self.stacked_widget, idx=4)
        self.cam5 = CameraWidget(camera_ip[4], self.stacked_widget, idx=5)
        self.cam6 = CameraWidget(camera_ip[5], self.stacked_widget, idx=6)

        widget_1 = DashBoard(self.cam1, self.cam2, self.cam3, self.cam4, self.cam5, self.cam6, self.stacked_widget)
        widget_2 = ZoneConfig(self.cam1, self.stacked_widget, 1)
        widget_3 = ZoneConfig(self.cam2, self.stacked_widget, 2)
        widget_4 = ZoneConfig(self.cam3, self.stacked_widget, 3)
        widget_5 = ZoneConfig(self.cam4, self.stacked_widget, 4)
        widget_6 = ZoneConfig(self.cam5, self.stacked_widget, 5)
        widget_7 = ZoneConfig(self.cam6, self.stacked_widget, 6)

        self.stacked_widget.addWidget(widget_1)
        self.stacked_widget.addWidget(widget_2)
        self.stacked_widget.addWidget(widget_3)
        self.stacked_widget.addWidget(widget_4)
        self.stacked_widget.addWidget(widget_5)
        self.stacked_widget.addWidget(widget_6)
        self.stacked_widget.addWidget(widget_7)

        self.showMaximized()

        QtCore.QTimer.singleShot(1 * 1000, self.hello)

    def hello(self):
        for i in range(1,7):
            self.stacked_widget.setCurrentIndex(i)
        self.stacked_widget.setCurrentIndex(0)

    def event(self, e):
        if e.type() in (QtCore.QEvent.Show, QtCore.QEvent.Resize):
            print("parent ", self.width(), self.height())

        return QtWidgets.QWidget.event(self, e)

    def closeEvent(self, event):
        logging.info("User clicked the red 'X' close button")
        close = QtWidgets.QMessageBox.question(self,"QUIT?","Are you sure you want to stop the application?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            logging.info("User closed the application")
            event.accept()
        else:
            logging.info("User didn't close the application")
            event.ignore()

        

# Cameras ip
tree = ET.parse('Configurations/cameras_ip.xml')
root = tree.getroot()
camera_ip = []
for elem in root:
    for subelem in elem:
        camera_ip.append(subelem.text)


# All configurations
tree = ET.parse('Configurations/all_configurations.xml')
root = tree.getroot()
all_configuration = []
for elem in root:
    for subelem in elem:
        all_configuration.append(subelem.text)




app2 = Flask(__name__)
cors = CORS(app2)

@app2.route("/", methods=["POST"])
def index():

    lock.acquire()
    try:
        start_time = time.time()
        np_array = np.frombuffer(request.data, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        id = int(request.headers["id"])
        gw.cameras[id-1].last_receive_time = time.time()
        gw.cameras[id-1].last_server_time = time.time()
        # gw.cameras[id-1].vehicle_count = request.headers["vehicle_count"]
        gw.cameras[id-1].server_online = True
        gw.cameras[id-1].online = True
        gw.cameras[id-1].flow_type = request.headers["flow_type"]
        gw.cameras[id-1].zone_occupancy = request.headers["zone_occupancy"]
        gw.cameras[id-1].fog_status = request.headers["fog_status"]

        gw.cameras[id-1].deque.append(frame)
        
    except Exception as e:
        logging.info(e)
    lock.release()
    
    response = {
                "show_zones": gw.cameras[id-1].show_zones,
    			"show_boxes": gw.cameras[id-1].show_bounding_box,
    			"all_zones": gw.cameras[id-1].zone_manager.all_zones
    		   }
    
    # jsonpickle.encode(response)
    return Response(response=str(response), status=200, mimetype="application/json")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setStyle(QtWidgets.QStyleFactory.create("plastique"))                            # applies to entire window 
    # app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))

    """Checks if duplicate instance of the application is launched"""
    try:
        mutex = win32event.CreateMutex(None, False, 'name')
        last_error = win32api.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:
            multi_error = MultipleInstanceError()

    except Exception as e:
        logging.info(e)

    login = Login()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        logging.info("Application Started")
        window = Window()
        gw.cameras = [window.cam1, window.cam2, window.cam3, window.cam4, window.cam5, window.cam6]

        threads = []
        max_instances = 6
        for n in range(1, max_instances+1):
            threads.append(Thread(target=app2.run, args=(all_configuration[0], int(all_configuration[1])+n, False,)))

        for thread in threads:
            thread.daemon = True
            thread.start()

        # window.show()
        sys.exit(app.exec_())