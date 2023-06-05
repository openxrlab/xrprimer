// TODO: enable vertex streaming via websocket
// export const UPDATE_WEBSOCKET_CONNECTED= "UPDATE_WEBSOCKET_CONNECTED"
export const UPDATE_CAMERA_PARAMS = "UPDATE_CAMERA_PARAMS"
export const UPDATE_CAMERA_RELOAD_FLAG = "UPDATE_CAMERA_RELOAD_FLAG"
export const UPDATE_BODY_MOTION = "UPDATE_BODY_MOTION"
export const UPDATE_BODY_RELOAD_FLAG = "UPDATE_BODY_RELOAD_FLAG"
export const UPDATE_IS_PLAYING = "UPDATE_IS_PLAYING"
export const UPDATE_FRAME_INDEX = "UPDATE_FRAME_INDEX"
export const UPDATE_FRAME_END = "UPDATE_FRAME_END"
export const UPDATE_INSTANT_FRAME = "UPDATE_INSTANT_FRAME"
export const UPDATE_DISPLAY_CAMERA_LABEL = "UPDATE_DISPLAY_CAMERA_LABEL"
export const UPDATE_CAMERA_GROUP_VISIBILITY = "UPDATE_CAMERA_GROUP_VISIBILITY"

// TODO: enable vertex streaming via websocket
// const msgpack = require("msgpack-lite");

// export function sendMessage(_webSocket: WebSocket, _type: String, _data){
//     if (_webSocket.readyState === WebSocket.OPEN) {
//         const data_packet = {
//           type: _type,
//           data: _data
//         };
//         const message = msgpack.encode(data_packet);
//         _webSocket.send(message);

//         return true;
//     }
//     else {
//       return false;
//     }
// }
