#! python
#
# Copyright 2021
# Authors: Mahdi Torkashvand

import cv2
import numpy as np

class ObjectDetector():
    """
    an object detection class.
    """
    def __init__(self, shape=(1, 512, 512), feat_size=2500, crop_size=300):
        self.shape = shape
        self.feat_size = feat_size
        self.crop_size = crop_size
        self.percentile = 1 - self.feat_size / (self.crop_size**2)
        self.out = np.zeros(self.shape[1:], dtype=np.uint8)
        self.y_slice = np.s_[self.shape[1] // 2 - self.crop_size // 2: self.shape[1] // 2 + self.crop_size // 2]
        self.x_slice = np.s_[self.shape[2] // 2 - self.crop_size // 2: self.shape[2] // 2 + self.crop_size // 2]
        self.bbox = (self.shape[2] // 2, self.shape[1] // 2, 10, 10)

    def set_shape(self, z, y, x):
        self.shape = (z, y, x)
        self.out = np.zeros(self.shape[1:], dtype=np.uint8)
        self.y_slice = np.s_[self.shape[1] // 2 - self.crop_size // 2: self.shape[1] // 2 + self.crop_size // 2]
        self.x_slice = np.s_[self.shape[2] // 2 - self.crop_size // 2: self.shape[2] // 2 + self.crop_size // 2]
        self.bbox = (self.shape[2] // 2, self.shape[1] // 2, 10, 10)

    def set_feat_size(self, feat_size):
        self.feat_size = feat_size
        self.percentile = 1 - self.feat_size / (self.crop_size**2)

    def set_crop_size(self, crop_size):
        if crop_size >= self.shape[1] or crop_size >= self.shape[2]:
            self.crop_size = min(self.shape[1], self.shape[2])
        else:
            self.crop_size = crop_size
        self.percentile = 1 - self.feat_size / (self.crop_size**2)
        self.y_slice = np.s_[self.shape[1] // 2 - self.crop_size // 2: self.shape[1] // 2 + self.crop_size // 2]
        self.x_slice = np.s_[self.shape[2] // 2 - self.crop_size // 2: self.shape[2] // 2 + self.crop_size // 2]

    def get_bbox(self, v):
        cropped_img = np.max(v, axis=0)[self.y_slice, self.x_slice]
        blurred = cv2.medianBlur(cropped_img, 5)
        blurred = blurred.astype(np.float32) / blurred.max()
        blurred = (blurred ** 3 * 255).astype(np.uint8)
        quantile = min(254, np.quantile(blurred, self.percentile))
        blurred[blurred<quantile]=0
        contours, _ = cv2.findContours(blurred, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) >= 1:
            contours = sorted(contours, key=cv2.contourArea)
            self.bbox = cv2.boundingRect(contours[-1])
            self.bbox = (self.bbox[0] + self.shape[2] // 2 - self.crop_size // 2,
                         self.bbox[1] + self.shape[1] // 2 - self.crop_size // 2,
                         self.bbox[2] , self.bbox[3])

        self.out[self.y_slice, self.x_slice] = blurred

class PIDController():
    """
    This PID controller calculates the velocity based
    on the current x,y value of the point of interest."""

    def __init__(self, Kp, Ki, Kd, SPx, SPy, camera_number, dt):

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.SPx = SPx
        self.SPy = SPy

        self.Ex = 0.0
        self.Ey = 0.0

        self.dt = dt

        self.Ix = 0.0
        self.Iy = 0.0

        self.axes_correction = np.array([[[1, 0], [0, -1]],
                                         [[0, 1], [1, 0]]])

        self.converter = self.axes_correction[camera_number-1]

    def set_rate(self, rate):
        self.dt = 1 / float(rate)

    def set_camera_number(self, camera_number):
        self.converter = self.axes_correction[camera_number-1]

    def set_center(self, SPx, SPy):
        self.SPx = SPx
        self.SPy = SPy

    def get_velocity(self, bbox):

        x = bbox[0] + bbox[2] // 2
        y = bbox[1] + bbox[3] // 2

        Ex = self.SPx - x
        Ey = self.SPy - y

        Px = self.Kp * Ex
        Py = self.Kp * Ey

        self.Ix = self.Ix + self.Ki * (Ex + self.Ex) * self.dt / 2
        self.Iy = self.Iy + self.Ki * (Ey + self.Ey) * self.dt / 2

        Dx = self.Kd * (Ex - self.Ex) / self.dt
        Dy = self.Kd * (Ey - self.Ey) / self.dt

        Vx = int(Px + self.Ix + Dx)
        Vy = int(Py + self.Iy + Dy)

        self.Ex = Ex
        self.Ey = Ey

        return np.matmul(self.converter, (Vx, Vy))