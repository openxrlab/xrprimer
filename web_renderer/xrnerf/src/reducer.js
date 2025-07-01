import * as Actions from './actions'

const initialState = {
    cameraFOV: 60,

    resolution: "720",

    webSocketConnected: false,

    webSocketUrl: 'ws://localhost:4567',

    renderType: 'rgb',

    renderResult: null,
};

const rootReducer = (state = initialState, action) => {
    switch(action.type){
        case Actions.UPDATE_CAMERA_FOV: {
            return{
                ...state,
                cameraFOV: action.data
            }
        }
        case Actions.UPDATE_RESOLUTION: {
            return{
                ...state,
                resolution: action.data
            }
        }
        case Actions.UPDATE_WEBSOCKET_CONNECTED: {
            return{
                ...state,
                webSocketConnected: action.data
            }
        }
        case Actions.UPDATE_RENDER_TYPE: {
            return{
                ...state,
                renderType: action.data
            }
        }
        case Actions.UPDATE_RENDER_RESULT: {
            return{
                ...state,
                render_result: action.data
            }
        }
        default: { // never
            return state;
        } 
            
    }
}

export default rootReducer;