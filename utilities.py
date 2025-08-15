import numpy as np

IDENTITY = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

INVERT_X = np.array([
    [-1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])

INVERT_Y = np.array([
    [1, 0, 0],
    [0, -1, 0],
    [0, 0, 1]
])

YAW = lambda yaw: np.array([
    [np.cos(yaw), 0, np.sin(yaw), 0],
    [0, 1, 0, 0],
    [-np.sin(yaw), 0, np.cos(yaw), 0],
    [0, 0, 0, 1]
])

PITCH = lambda pitch: np.array([
    [1, 0, 0, 0],
    [0, np.cos(pitch), -np.sin(pitch), 0],
    [0, np.sin(pitch), np.cos(pitch), 0],
    [0, 0, 0, 1]
])

ROLL = lambda roll: np.array([
    [np.cos(roll), -np.sin(roll), 0, 0],
    [np.sin(roll), np.cos(roll), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

TRANSLATE = lambda x, y, z: np.array([
    [1, 0, 0, x],
    [0, 1, 0, y],
    [0, 0, 1, z],
    [0, 0, 0, 1]
])

AXIS = lambda x, y, z: np.array([
    [x],
    [y],
    [z],
    [1]
])

TRANSPOSE_3D = lambda x, y, z, l: np.array([
    [x, y, z]
])

def get_rotation_matrix(yaw, pitch, roll):
    """
    Gets the cumulative rotation matrix across each axis as a quaternion.
    :param yaw: the degree of rotation about the Y axis (like looking left and right)
    :param pitch: the degree of rotation about the X axis (like looking up and down)
    :param roll: the degree of rotation about the Z axis (like tilting your head)
    """
    R = np.dot(YAW(yaw), (PITCH(pitch), ROLL(roll)))
    return R

def get_transform(translate: np.ndarray, axis: np.ndarray, yaw_pitch_roll: np.ndarray):
    """
    Gets the final transformation matrix for a change in position and orientation.
    :param translate: a 1x3 vector that represents the change in position of the axis
    :param axis: a 1x3 vector that represents the center of the rotations
    :param yaw_pitch_roll: a 1x3 array that holds the changes to orientation as degrees
    :return: a 4x4 Matrix given by T(p) x R x T(-p)
    """
    R = get_rotation_matrix(*yaw_pitch_roll)
    T = TRANSLATE(*translate)
    p = AXIS(*axis)
    Tp = np.dot(T, p)
    Tp_b = np.dot(T, np.subtract(IDENTITY, p))
    return np.dot(Tp, np.dot(R, Tp_b))

def apply_transform(translate: np.ndarray, axis, np.ndarray, yaw_pitch_roll: np.ndarray, current_matrix: np.ndarray):
    """
    Applies a new transformation to an existing transformation
    :return: a 4x4 matrix given by M_new x M_old. Represents the cumulative changes to the solid.
    """
    M_new = get_transform(translate, axis, yaw_pitch_roll)
    return np.dot(M_new, current_matrix)
    
def world_coordinates(vertex_coordinates: np.ndarray, transformation: np.ndarray):
    """
    Maps relative coordinates to the true absolute coordinates for vertex
    :return: a 1x3 array representing the final position of a vertex in space
    """
    # Transpose the coordinates and add the 4th dimension
    point = AXIS(*vertex_coordinates)
    world_coordinates = np.dot(transformation, point)
    return TRANSPOSE_3D(*world_coordinates.flatten())
