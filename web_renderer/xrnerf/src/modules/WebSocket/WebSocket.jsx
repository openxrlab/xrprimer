import { createContext, useEffect } from "react";
import { useDispatch, useSelector } from 'react-redux';

import PropTypes from 'prop-types';

import { UPDATE_WEBSOCKET_CONNECTED } from "../../actions";

const WebSocketContext = createContext(null);

export { WebSocketContext };

export default function WebSocketContextFunction(props){
    const { children } = props;

    const dispatch = useDispatch();

    let ws = null;
    let socket = null;

    const webSocketUrl = useSelector(
        (state) => state.webSocketUrl,
    );

    const connect = () => {
        console.log("websocket url: " + webSocketUrl);
        try{
            socket = new WebSocket(webSocketUrl);
        } catch(error){
            socket = new WebSocket('ws://localhost:4567');
        }
        socket.binaryType = 'arraybuffer';
        socket.onopen = () => {
            console.log("websocket connected");
            dispatch({
                type: UPDATE_WEBSOCKET_CONNECTED,
                data: true,
            });
        };

        socket.onclose = () => {
            console.log("websocket disconnected");
            dispatch({
                type: UPDATE_WEBSOCKET_CONNECTED,
                data: false,
            });
        };

        socket.onerror = (err) => {
            console.error("Socket error occured: ", err.message, "Closing socket");
            socket.close();
        };
        
        return socket;
    };

    useEffect(() => {
        return () => {
            if (socket !== null) {
                socket.close();
            }
        };
    }, [socket]);

    connect();

    ws = {
        socket,
    };

    return (
        <WebSocketContext.Provider value={ws}>
            {children}
        </WebSocketContext.Provider>
    );
}

WebSocketContextFunction.propTypes = {
    children: PropTypes.node.isRequired,
};