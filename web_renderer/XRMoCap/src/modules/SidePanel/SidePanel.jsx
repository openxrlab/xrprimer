import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import {
    Stack, Button, Box, Grid,
    ListItemButton, ListItemIcon, List, ListItemText, IconButton, ListItem, Collapse
} from '@mui/material';

import { UPDATE_BODY_MOTION, UPDATE_BODY_RELOAD_FLAG, UPDATE_CAMERA_GROUP_VISIBILITY, UPDATE_DISPLAY_CAMERA_LABEL, UPDATE_CAMERA_RELOAD_FLAG,  UPDATE_CAMERA_PARAMS } from '../../actions'
import * as BABYLON from '@babylonjs/core';

import { CameraAltTwoTone, VisibilityOutlined, VisibilityOffOutlined, ExpandLess, ExpandMore, SpeakerNotes, SpeakerNotesOff } from '@mui/icons-material'

export function SidePanel(){ 
    const dispatch = useDispatch();

    // TODO: enable vertex streaming via websocket
    // const webSocket = React.useContext(WebSocketContext).socket;
    // const webSocketConnected = useSelector(
    //     (state) => state.webSocketConnected
    // );
    // const webSocketConnectedText = webSocketConnected ? "connected" : "disconnected";
    // const webSocketConnectedColor = webSocketConnected ? "#008000" : "#DC143C";

    const cameraParams = useSelector(
        (state) => state.cameraParams
    );

    const cameraGroupVisibility = useSelector(
        (state) => state.cameraGroupVisibility
    );

    const [cameraListOpened, setCameraListOpened] = React.useState(true);
    const [cameraMeshGroupVisible, setcameraMeshGroupVisible] = React.useState(true);
    const [cameraLabelGroupVisible, setcameraLabelGroupVisible] = React.useState(false);
    
    const toggleCameraListOpened = () => {
        setCameraListOpened(!cameraListOpened);
    }

    const togglecameraMeshGroupVisible = () => {
        setcameraMeshGroupVisible(!cameraMeshGroupVisible);

        const _cameraGroupVisibility = JSON.parse(cameraGroupVisibility);
        for(let key in _cameraGroupVisibility){
            _cameraGroupVisibility[key]['mesh_visible'] = !cameraMeshGroupVisible;
        }

        dispatch({
            type: UPDATE_CAMERA_GROUP_VISIBILITY,
            data: JSON.stringify(_cameraGroupVisibility)
        });
    }

    const togglecameraLabelGroupVisible = () => {
        setcameraLabelGroupVisible(!cameraLabelGroupVisible);

        const _cameraGroupVisibility = JSON.parse(cameraGroupVisibility);
        for(let key in _cameraGroupVisibility){
            _cameraGroupVisibility[key]['label_visible'] = !cameraLabelGroupVisible;
        }

        dispatch({
            type: UPDATE_CAMERA_GROUP_VISIBILITY,
            data: JSON.stringify(_cameraGroupVisibility)
        });
    }
    
    const cameraFileInput = React.useRef(null);
    const handleCameraFileUploadClick = () => {
        cameraFileInput.current.click();
    }

    const handleCameraFileInput = (event) => {        
        function readCameraFiles(file_list){
            let cameraParamPromises = [];
            for (let file of file_list) {
                let cameraParamPromise = new Promise(resolve => {
                    let reader = new FileReader();
                    reader.readAsText(file);
                    reader.onload = (res) => {
                        resolve(JSON.parse(res.target.result));
                    }
                });
                cameraParamPromises.push(cameraParamPromise);
            }
            Promise.all(cameraParamPromises).then(cameraParamContents => {
                // fileContents will be an array containing
                // the contents of the files, perform the
                // character replacements and other transformations
                // here as needed
                if(cameraParamContents.length !== 0){
                    let cameraGroupVisibilityContents = {};
                    cameraParamContents.forEach((cameraParamContent) => {
                        cameraGroupVisibilityContents[cameraParamContent['name']] = {
                            'mesh_visible': true,
                            'label_visible': false
                        }
                    });

                    dispatch({
                        type: UPDATE_CAMERA_PARAMS,
                        data: cameraParamContents
                    });
        
                    dispatch({
                        type: UPDATE_CAMERA_RELOAD_FLAG,
                        data: true
                    });
                    
                    dispatch({
                        type: UPDATE_CAMERA_GROUP_VISIBILITY,
                        data: JSON.stringify(cameraGroupVisibilityContents)
                    });
                }
            });
        }
        const uploadedFiles = event.target.files;
        readCameraFiles(uploadedFiles);
    }

    const bodyFileInput = React.useRef(null);
    const handleBodyFileUploadClick = () => {
        bodyFileInput.current.click();
    }

    const handleBodyFileInput = (event) => {
        const uploadedFile = event.target.files[0];

        const filename = uploadedFile.name;
        const blob = new Blob([uploadedFile]);
        BABYLON.FilesInput.FilesToLoad[filename] = blob;
        dispatch({
            type: UPDATE_BODY_RELOAD_FLAG,
            data: true
        });

        dispatch({
            type: UPDATE_BODY_MOTION,
            data: filename
        });
    }
    
    return (
        <div className='SidePanel'>
            <Button
                className='SidePanel-refresh-page'
                variant="outlined"
                onClick={() => {
                    // disable eslint parsing error: https://blog.csdn.net/qq_43440532/article/details/121304188
                    // eslint-disable-next-line 
                    location.reload();
                }}
            >
                Refresh Page
            </Button>

            <Button
                className='SidePanel-load-camera'
                id='load-camera'
                variant="outlined"
                onClick={handleCameraFileUploadClick}
            >
                Load Camera
                <input
                    type="file"
                    accept=".json"
                    name="Camera"
                    onChange={handleCameraFileInput}
                    hidden
                    multiple
                    ref={cameraFileInput}
                />
            </Button>

            <Button
                className='SidePanel-load-body'
                id='load-body'
                variant="outlined"
                onClick={handleBodyFileUploadClick}
            >
                Load Body
                <input
                    type="file"
                    accept=".glb"
                    name="Camera"
                    onChange={handleBodyFileInput}
                    hidden
                    multiple
                    ref={bodyFileInput}
                />
            </Button>

            {/* TODO: vertex streaming via websocket */}
            {/* <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                <div 
                    className='SidePanel-websocket-state'
                >
                    <b>WebSocket State: </b>
                    <font color={webSocketConnectedColor}> 
                        {webSocketConnectedText}
                    </font>
                </div>
            </Stack> */}
            
            <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                <div className='SidePanel-frame-rate' >
                    <b>Frame Rate: </b>
                    <font id='fpsDiv'>
                        0
                    </font>
                </div>
            </Stack>

            <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                <div className='SidePanel-canvas-size' >
                    <b>Canvas Size: </b>
                    <font id='canvasSizeDiv'>
                        <font id='canvasSizeX'>0.0</font>x<font id='canvasSizeY'>0.0</font>
                    </font>
                </div>
            </Stack>

            <div className='SidePanelPanel-metrics'>
                <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                    <b>Translation: </b>
                    <Box sx={{ flexGrow: 1 }}>
                        <Grid container spacing={1}>
                            <Grid container item spacing={1}>
                                <React.Fragment>
                                    <Grid item xs={4}>
                                        <Button variant='outlined' size='small'>
                                            <font id='cameraTransX'>0.0</font>
                                        </Button>
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Button variant='outlined' size='small'>
                                            <font id='cameraTransY'>0.0</font>
                                        </Button>
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Button variant='outlined' size='small'>
                                            <font id='cameraTransZ'>0.0</font>
                                        </Button>
                                    </Grid>
                                </React.Fragment>
                            </Grid>
                        </Grid>
                    </Box>
                </Stack>

                <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                    <b>Rotation: </b>
                    <div id='cameraRotationDiv'></div>
                    <Grid container spacing={1}>
                        <Grid container item spacing={1}>
                            <React.Fragment>
                                <Grid item xs={4}>
                                    <Button variant='outlined' size='small'>
                                        <font id='cameraRotationX'>0.0</font>
                                    </Button>
                                </Grid>
                                <Grid item xs={4}>
                                    <Button variant='outlined' size='small'>
                                        <font id='cameraRotationY'>0.0</font>
                                    </Button>
                                </Grid>
                                <Grid item xs={4}>
                                    <Button variant='outlined' size='small'>
                                        <font id='cameraRotationZ'>0.0</font>
                                    </Button>
                                </Grid>
                            </React.Fragment>
                        </Grid>
                    </Grid>
                </Stack>
            </div>
            
            <ListItem >
                <ListItemButton onClick={toggleCameraListOpened}>
                    <IconButton>
                        <CameraAltTwoTone color='primary'/>
                    </IconButton>

                    <ListItemText primary="Cameras" />
                </ListItemButton>
                
                <IconButton 
                    aria-label="visibility" 
                    onClick={()=>{
                        togglecameraMeshGroupVisible();
                    }}
                >
                    {cameraMeshGroupVisible ? <VisibilityOutlined color='primary' /> : <VisibilityOffOutlined color='primary'/>}
                </IconButton>

                <IconButton 
                    aria-label="visibility" 
                    onClick={()=>{
                        togglecameraLabelGroupVisible();
                        dispatch({
                            type: UPDATE_DISPLAY_CAMERA_LABEL,
                            data: !cameraLabelGroupVisible
                        });
                    }}
                >
                    {cameraLabelGroupVisible ? <SpeakerNotes color='primary' /> : <SpeakerNotesOff color='primary'/>}
                </IconButton>

                {cameraListOpened ? <ExpandLess/> : <ExpandMore/>}
            </ListItem>

            <Collapse in={cameraListOpened} timeout="auto">
                <List>
                    {cameraParams ? cameraParams.map((cameraParam) => {
                        return (
                            <CameraItem 
                                name={cameraParam['name']}
                                // Each child in a list should have a unique “key” prop
                                // https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key
                                key={cameraParam['name']}
                                cameraMeshGroupVisible={cameraMeshGroupVisible}
                                cameraLabelGroupVisible={cameraLabelGroupVisible}
                                cameraGroupVisibility={cameraGroupVisibility}
                                dispatch={dispatch}
                            />
                        )
                    }) : null}
                </List>
            </Collapse>
        </div>
    );
}

export type CameraItemProps = {
    name: string,
    cameraMeshGroupVisible: Boolean,
    cameraLabelGroupVisible: Boolean,
    cameraGroupVisibility: Any,
    dispatch: Any
}

function CameraItem(props: CameraItemProps){
    const name = props.name;
    const cameraGroupVisibility = JSON.parse(props.cameraGroupVisibility);
    const cameraMeshGroupVisible = props.cameraMeshGroupVisible;
    const cameraLabelGroupVisible = props.cameraLabelGroupVisible;
    const dispatch = props.dispatch;

    let [meshVisible, setMeshVisible] = React.useState(cameraGroupVisibility[name]['mesh_visible']);
    let [labelVisible, setLabelVisible] = React.useState(cameraGroupVisibility[name]['label_visible']);

    const toggleMeshVisible = () => {
        setMeshVisible(!meshVisible);
    }
    
    const toggleLabelVisible = () =>{
        setLabelVisible(!labelVisible);
    }

    React.useEffect(() => {
        setMeshVisible(cameraMeshGroupVisible);
        setLabelVisible(cameraLabelGroupVisible);
    }, [cameraMeshGroupVisible, cameraLabelGroupVisible]);


    React.useEffect(() => {        
        let _cameraGroupVisibility = cameraGroupVisibility;
        _cameraGroupVisibility[name] = {
            'mesh_visible': meshVisible,
            'label_visible': labelVisible
        };

        dispatch({
            type: UPDATE_CAMERA_GROUP_VISIBILITY,
            data: JSON.stringify(_cameraGroupVisibility)
        })

    }, [meshVisible, labelVisible, dispatch, name, cameraGroupVisibility]);

    return(
        <>
            <ListItem>
                <ListItemIcon>
                    <CameraAltTwoTone color='primary'/>
                </ListItemIcon>

                <ListItemText primary={name} />

                <IconButton aria-label="visibility" onClick={toggleMeshVisible}>
                    {meshVisible ? <VisibilityOutlined color='primary' /> : <VisibilityOffOutlined color='primary'/>}
                </IconButton>

                <IconButton aria-label="visibility" onClick={toggleLabelVisible}>
                    {labelVisible ? <SpeakerNotes color='primary' /> : <SpeakerNotesOff color='primary'/>}
                </IconButton>
            </ListItem>
        </>
    )
}