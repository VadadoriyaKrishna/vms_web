
# Imports
import numpy as np
import cv2
import pickle
from PIL import *
import os
import json
import requests   #
import logging


class ZoneManager:

    # def __init__(self, index_val = 0, config_file_path):
    #     self.drawing = True
    #     self.point = (0, 0)
    #     self.all_points, self.all_zones = [], {}
    #     self.index = index_val
    #     self.alpha = 0.4
    #     self.mouse_pos = (0, 0)
    #     self.load = True
    #     self.load_data(config_file_path)

    def __init__(self, idx=None, index_val = 0):
        # print('weufgwei')
        self.drawing = True
        self.point = (0, 0)
        self.all_points, self.all_zones = [], {}
        self.draw_zones = False
        self.index = index_val
        self.alpha = 0.2
        self.mouse_pos = (0, 0)
        # self.load_data()
        self.idx = idx
        self.unsaved_changes = False
        self.create_file()
        # print(self.zone_target_ip)

    def make_points(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing is True:
                point = (x, y)
                self.all_points.append(point)

        if event == cv2.EVENT_MOUSEMOVE:
            mouse_pos = (x, y)

    def centroid(self, vertexes):
        _x_list = [vertex[0] for vertex in vertexes]
        _y_list = [vertex[1] for vertex in vertexes]
        _len = len(vertexes)
        _x = sum(_x_list) / _len
        _y = sum(_y_list) / _len
        return (int(_x), int(_y))

    def write_data(self, data_path=None):
        if data_path is None:
            data_path="Configs/vms_"+str(self.idx)+"_zone_config.json"
        try:
            with open(data_path, 'w') as handle:
                json.dump(self.all_zones, handle)

            # payload={'configuration':str(self.all_zones)}
            
            # try:
            #     r = requests.get(self.zone_target_ip, params=payload)
            #     print("Trying to send.")

            # except Exception as e:
            #     print("Exception:", e)
            # # print(r.text)

        except Exception as e:
            logging.error("Could not save zone", exc_info=True)

    def load_data(self, data_path=None):
        if data_path is None:
            data_path="Configs/vms_"+str(self.idx)+"_zone_config.json"
        # print("Zones loaded.")
        try:
            if os.path.exists(data_path):
                with open(data_path, 'r') as handle:
                    self.all_zones = json.load(handle)
                    if self.all_zones == {}:
                        # handle.close()
                        # os.remove(data_path)
                        self.index = 0
                    else:
                        self.index = int(list(self.all_zones)[-1]) + 1
            else:
                print("FILE not found.")

        except Exception as e:
            logging.error("Could not load zone", exc_info=True)

    def run(self, frame, width, height):

        try:
            frame = cv2.resize(frame, (width, height))
        except:
            pass
        # self.all_points.append(point)
        # cv2.namedWindow("vms 2.0")
        # cv2.setMouseCallback("vms 2.0", self.make_points)
        colours = [(0, 0, 255), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255), (255, 255, 255), (102, 51, 0), (0, 51, 204), (0, 102, 0), (255, 0, 255), (102, 102, 153), (0, 51, 153), (153, 204, 0), (102, 0, 102), (153, 102, 51), (102, 153, 153), (255, 153, 255), (0, 204, 153), (102, 255, 51), (51, 51, 255)]

        overlay = frame.copy()

        # print(self.all_zones)

        for n, point in enumerate(self.all_points):
            cv2.circle(frame, point, 5, colours[self.index], -1)
            cv2.putText(frame, str(n + 1), (point[0] - 5, point[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 255, 255), 2, cv2.LINE_AA)

        if len(self.all_points) >= 3:
            cv2.fillPoly(overlay, [np.array(self.all_points)], colours[self.index])
            cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)

        # for zone_id in self.all_zones.keys():
        for zone_id in list(self.all_zones):
            overlay = frame.copy()
            cv2.fillPoly(overlay, [np.array(self.all_zones[zone_id], dtype=np.int32)], colours[int(zone_id)])
            cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)
            cv2.putText(frame, "ZONE: {}".format(int(zone_id) + 1), self.centroid(self.all_zones[zone_id]),
                        cv2.FONT_HERSHEY_PLAIN,
                        1, (255, 255, 255), 1, cv2.LINE_AA)

        y_coord = 120
        x_coord = 1370
        colour = (255, 255, 255)
        """
        cv2.putText(frame, "<<ZONE MARKER>>", (x_coord + 30, y_coord), cv2.FONT_HERSHEY_PLAIN, 3,
                    colour, 1, cv2.LINE_AA)
        cv2.putText(frame, "A - Exit Draw Mode", (x_coord + 30, y_coord + 40), cv2.FONT_HERSHEY_PLAIN, 2,
                    colour, 1, cv2.LINE_AA)

        cv2.putText(frame, "S - Confirm Zone.", (x_coord + 30, y_coord + 80), cv2.FONT_HERSHEY_PLAIN, 2, colour, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, "R - Reset Zone.", (x_coord + 30, y_coord + 120), cv2.FONT_HERSHEY_PLAIN, 2, colour, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, "E - Save Zones.", (x_coord + 30, y_coord + 160), cv2.FONT_HERSHEY_PLAIN, 2, colour, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, "W - Load Zones.", (x_coord + 30, y_coord + 200), cv2.FONT_HERSHEY_PLAIN, 2, colour, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, "X - Delete Zones.", (x_coord + 30, y_coord + 240), cv2.FONT_HERSHEY_PLAIN, 2, colour, 1,
                    cv2.LINE_AA)
        cv2.putText(frame, "NUMBER OF ZONES: {}".format(len(self.all_zones.keys())), (x_coord + 30, y_coord + 340),
                    cv2.FONT_HERSHEY_PLAIN, 1, colour, 1, cv2.LINE_AA)
        """
        self.all_zones
        # self.load_data()
        # cv2.imshow("vms 2.0", frame)
        return frame


        # if key_press == ord('s'):
        #     if len(self.all_points) > 2:
        #         self.all_zones[self.index] = self.all_points
        #         self.index += 1
        #     self.all_points = []
        # if key_press == ord('r'):
        #     self.all_points = []
        # if key_press == ord('e'): self.write_data()
        # if key_press == ord('w'): self.load_data()
        # if key_press == ord('x'): self.all_zones = {}

    def create_file(self, data_path=None):
        if data_path is None:
            data_path="Configs/vms_"+str(self.idx)+"_zone_config.json"
        if not os.path.exists(data_path):
            self.all_zones = {}
            with open(data_path, 'w') as handle:
                json.dump(self.all_zones, handle)
                print("FILE CREATED.")
        self.load_data()

    def make_points2(self, point):
        if self.draw_zones and point != (-1,-1):
            self.all_points.append(point)
            self.unsaved_changes = True

    def confirm(self):
        if len(self.all_points) > 2:
            self.all_zones[self.index] = self.all_points
            self.index += 1
        self.all_points = []
        self.unsaved_changes = True


    def reset(self):
        self.all_points = []
        self.unsaved_changes = False

    def save(self):
        self.write_data()
        self.unsaved_changes = False

    def load(self):
        self.load_data()
        self.unsaved_changes = False

    def delete(self, data_path=None):
        if data_path is None:
            data_path="Configs/vms_"+str(self.idx)+"_zone_config.json"
        try:
            if os.path.exists(data_path):
                self.all_zones = {}
                with open(data_path, 'w') as handle:
                    json.dump(self.all_zones, handle)

            self.index = 0
            self.unsaved_changes = False
        
        except Exception as e:
            logging.error("Could not delete zones", exc_info=True)