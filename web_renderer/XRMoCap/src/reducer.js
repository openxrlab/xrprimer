import * as Actions from './actions'

const initialState = {
    // TODO: enable vertex streaming via websocket
    // webSocketConnected: false,

    webSocketUrl: 'ws://localhost:4567',

    cameraParams: [],

    cameraReloadFlag: false,

    displayCameraLabel: false,

    bodyMotion: null,

    bodyReloadFlag: false,

    isPlaying: false,

    frameIndex: -1,

    frameEnd: 0,

    instantFrame: false,

    // contains the metadata of camera group visibility, e.g.
    // {
    //   'camera1': {
    //        'mesh_visible': true, 
    //        'label_visible': true
    //   },
    //   ...
    // }
    cameraGroupVisibility: JSON.stringify({}),
};

const rootReducer = (state = initialState, action) => {
    switch(action.type){
        case Actions.UPDATE_CAMERA_PARAMS:{
            return{
                ...state,
                cameraParams: action.data
            }
        }
        case Actions.UPDATE_CAMERA_RELOAD_FLAG:{
            return{
                ...state,
                cameraReloadFlag: action.data
            }
        }
        case Actions.UPDATE_BODY_MOTION:{
            return{
                ...state,
                bodyMotion: action.data
            }
        }
        case Actions.UPDATE_BODY_RELOAD_FLAG: {
            return{
                ...state,
                bodyReloadFlag: action.data
            }
        }
        case Actions.UPDATE_IS_PLAYING: {
            return{
                ...state,
                isPlaying: action.data
            }
        }
        case Actions.UPDATE_FRAME_INDEX: {
            return{
                ...state,
                frameIndex: action.data
            }
        }
        case Actions.UPDATE_FRAME_END: {
            return{
                ...state,
                frameEnd: action.data
            }
        }
        case Actions.UPDATE_INSTANT_FRAME: {
            return{
                ...state,
                instantFrame: action.data
            }
        }
        case Actions.UPDATE_DISPLAY_CAMERA_LABEL:{
            return{
                ...state,
                displayCameraLabel: action.data
            }
        }
        case Actions.UPDATE_CAMERA_GROUP_VISIBILITY:{
            return{
                ...state,
                cameraGroupVisibility: action.data
            }
        }
        // TODO: enable vertex streaming via websocket
        // case Actions.UPDATE_WEBSOCKET_CONNECTED: {
        //     return{
        //         ...state,
        //         webSocketConnected: action.data
        //     }
        // }
        default: { // never
            return state;
        }
    }
}

export default rootReducer;