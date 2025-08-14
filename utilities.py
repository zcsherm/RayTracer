import numpy as np

IDENTITY = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])

YAW = lambda yaw: np.array([
    [np.cos(yaw), 0, np.sin(yaw)],
    [0, 1, 0],
    [-np.sin(yaw), 0, np.cos(yaw)]
])

PITCH = lambda pitch: np.array([
    [1, 0, 0],
    [0, np.cos(pitch), -np.sin(pitch)],
    [0, np.sin(pitch), np.cos(pitch)]
])

ROLL = lambda roll: np.array([
    [np.cos(roll), -np.sin(roll), 0],
    [np.sin(roll), np.cos(roll), 0],
    [0, 0, 1]
])

def rotate(yaw, pitch, roll, vector):
    R = np.dot(YAW(yaw), (PITCH(pitch), ROLL(roll)))
    return np.dot(R, vector)