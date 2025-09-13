// TODO: enable vertex streaming via websocket
// import { useContext, useEffect } from "react";
// import { useDispatch } from "react-redux";
// import { WebSocketContext } from "./WebSocket";

// import { UPDATE_RENDER_RESULT } from "../../actions";

// const msgpack = require('msgpack-lite');

// const WebSocketListener = () => {
//     const socket = useContext(WebSocketContext).socket;
//     const dispatch = useDispatch();

//     useEffect(() => {
//         socket.addEventListener('message', (originalCmd) => {
//             const cmd = msgpack.decode(new Uint8Array(originalCmd.data));
//             if(cmd.type === UPDATE_RENDER_RESULT){
//                 dispatch({
//                     type: UPDATE_RENDER_RESULT,
//                     data: cmd.data
//                 })
//             }
//         })
//     }, [socket, dispatch]);
// }

// export { WebSocketListener };