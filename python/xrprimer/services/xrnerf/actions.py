from enum import Enum


class ViewerActionEnum(str, Enum):
    UPDATE_CAMERA_TRANSLATION = 'UPDATE_CAMERA_TRANSLATION'
    UPDATE_CAMERA_ROTATION = 'UPDATE_CAMERA_ROTATION'
    UPDATE_CAMERA_FOV = 'UPDATE_CAMERA_FOV'
    UPDATE_RESOLUTION = 'UPDATE_RESOLUTION'
    UPDATE_RENDER_TYPE = 'UPDATE_RENDER_TYPE'


class BackendActionsEnum(str, Enum):
    UPDATE_STATE = 'UPDATE_STATE'
    UPDATE_RENDER_RESULT = 'UPDATE_RENDER_RESULT'
    PING = 'ping'
