export const UPDATE_CAMERA_TRANSLATION = "UPDATE_CAMERA_TRANSLATION"
export const UPDATE_CAMERA_ROTATION = "UPDATE_CAMERA_ROTATION"
export const UPDATE_CAMERA_FOV = "UPDATE_CAMERA_FOV"
export const UPDATE_RESOLUTION = "UPDATE_RESOLUTION"
export const UPDATE_RENDER_TYPE = "UPDATE_RENDER_TYPE"
export const UPDATE_RENDER_RESULT = "UPDATE_RENDER_RESULT"
export const UPDATE_CANVAS_SIZE = "UPDATE_CANVAS_SIZE"
export const UPDATE_WEBSOCKET_CONNECTED= "UPDATE_WEBSOCKET_CONNECTED"

const msgpack = require("msgpack-lite");

export function sendMessage(_webSocket: WebSocket, _type: String, _data){
    if (_webSocket.readyState === WebSocket.OPEN) {
        const data_packet = {
          type: _type,
          data: _data
        };
        const message = msgpack.encode(data_packet);
        _webSocket.send(message);

        return true;
    }
    else {
      return false;
    }
}
