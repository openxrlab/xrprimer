import * as Actions from './actions'

const initialState = {
    cameraRotation: [
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0
    ],

    cameraTranslation: [0.0, 0.0, 0.0],

    cameraFOV: 60,

    resolution: "720",

    webSocketConnected: false,

    webSocketUrl: 'ws://localhost:4567',

    renderType: 'rgb',

    canvasSize: [1920, 1080],

    renderResult: null,
};

const rootReducer = (state = initialState, action) => {
    switch(action.type){
        case Actions.UPDATE_CAMERA_TRANSLATION:{
            return{
                ...state,
                cameraTranslation: action.data
            }
        }
        case Actions.UPDATE_CAMERA_ROTATION:{
            return{
                ...state,
                cameraRotation: action.data
            }
        }
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
        case Actions.UPDATE_CANVAS_SIZE: {
            return{
                ...state,
                canvasSize: action.data
            }
        }
        default: { // never
            return state;
        } 
            
    }
}

export default rootReducer;