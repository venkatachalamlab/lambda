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
    def __init__(self, shape=(1, 512, 512), feat_size=2500):
        self.shape = shape
        self.feat_size = feat_size
        self.percentile = 1 - self.feat_size / np.prod(self.shape)
        self.out = np.zeros(self.shape[1:], dtype=np.uint8)
        self.h_slice = np.s_[self.shape[1] // 2 - 150: self.shape[1] // 2 + 150]
        self.w_slice = np.s_[self.shape[2] // 2 - 150: self.shape[2] // 2 + 150]
        self.bbox = (0, 0, 0, 0)

    def set_shape(self, shape):
        self.shape = shape
        self.out = np.zeros(self.shape[1:], dtype=np.uint8)
        self.h_slice = np.s_[self.shape[1] // 2 - 150: self.shape[1] // 2 + 150]
        self.w_slice = np.s_[self.shape[2] // 2 - 150: self.shape[2] // 2 + 150]
        self.percentile = 1 - self.feat_size / np.prod(self.shape)

    def set_feat_size(self, feat_size):
        self.feat_size = feat_size
        self.percentile = 1 - self.feat_size / np.prod(self.shape)

    def get_bbox(self, v):
        cropped_img = np.max(v, axis=0)[self.h_slice, self.w_slice]
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

        self.out[self.h_slice, self.w_slice] = blurred

class PIDController():
    """
    This PID controller calculates the velocity based
    on the current x,y value of the point of interest."""

    def __init__(self, Kp, Ki, Kd, SPx, SPy, index, dt=0.025):

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.SPx = SPx
        self.SPy = SPy

        self.Ex = 0.0
        self.Ey = 0.0

        self.Ix = 0.0
        self.Iy = 0.0

        self.dt = dt

        self.axes_correction = np.array([[[1, 0], [0, 1]],
                                         [[0, 1], [1, 0]]])

        self.index = index

    def get_velocity(self, bbox):

        x = bbox[0] + bbox[2] // 2
        y = bbox[1] + bbox[3] // 2

        Ex = self.SPx - x
        Ey = self.SPy - y


        Px = self.Kp * Ex
        Py = self.Kp * Ey

        self.Ix = self.Ix + self.Ki * Ex * self.dt
        self.Iy = self.Iy + self.Ki * Ey * self.dt

        Dx = self.Kd * (Ex - self.Ex) / self.dt
        Dy = self.Kd * (Ey - self.Ey) / self.dt

        Vx = Px + int(self.Ix + Dx)
        Vy = Py + int(self.Iy + Dy)

        self.Ex = Ex
        self.Ey = Ey

        return np.matmul(self.axes_correction[self.index], (Vx, Vy))