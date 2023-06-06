import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import {
    Stack, Slider, Button, Box, Grid, Select, FormControl,
    Radio, RadioGroup, FormControlLabel
} from '@mui/material';

import { Menu, MenuItem } from 'react-pro-sidebar';

import { sendMessage } from '../../actions'
import { UPDATE_CAMERA_FOV, UPDATE_RENDER_TYPE, UPDATE_RESOLUTION } from "../../actions";
import { WebSocketContext } from "../WebSocket/WebSocket";
// import * as BABYLON from '@babylonjs/core';

export function SidePanel(){
    // const {
    //     webSocket
    // } = props;
    const webSocket = React.useContext(WebSocketContext).socket;
    const dispatch = useDispatch();

    const cameraFOV = useSelector(
        (state) => state.cameraFOV
    );

    const webSocketConnected = useSelector(
        (state) => state.webSocketConnected
    );

    const renderType = useSelector(
        (state) => state.renderType
    );

    const resolution = useSelector(
        (state) => state.resolution
    );

    const webSocketConnectedText = webSocketConnected ? "connected" : "disconnected";
    const webSocketConnectedColor = webSocketConnected ? "#008000" : "#DC143C";
    console.log(Date.now());

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

            <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                <div 
                    className='SidePanel-websocket-state'
                >
                    <b>WebSocket State: </b>
                    <font color={webSocketConnectedColor}> 
                        {webSocketConnectedText}
                    </font>
                </div>
            </Stack>
            
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
                        <font id='canvasSizeX'>0</font>x<font id='canvasSizeY'>0</font>
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

            <div className='SidePanel-camera-props'>
                <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                    <p>Camera FOV</p>
                    <Slider
                        value={cameraFOV}
                        step={1}
                        min={1}
                        max={179}
                        onChange={(event, value) => {
                            dispatch({
                                type: UPDATE_CAMERA_FOV,
                                data: value
                            })
                            sendMessage(webSocket, UPDATE_CAMERA_FOV, value)
                        }}
                    />
                    <p>{cameraFOV}</p>
                </Stack>
                <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                    <p>Render Type</p>
                    <FormControl>
                        <Menu>
                            <Select
                                labelId='render-type-select'
                                value={renderType}
                                onChange={(event) => {
                                    const value = event.target.value

                                    dispatch({
                                        type: UPDATE_RENDER_TYPE,
                                        data: value
                                    })
                                    sendMessage(webSocket, UPDATE_RENDER_TYPE, value)
                                }}
                            >
                                <MenuItem value='rgb'>RGB</MenuItem>
                                <MenuItem value='rgb_mask'>RGB+MASK</MenuItem>
                                <MenuItem value='depth'>DEPTH</MenuItem>
                            </Select>
                        </Menu>
                    </FormControl>
                </Stack>
                <Stack spacing={2} direction="row" sx={{mb:1}} alignItems="center">
                    <p>Resolution:</p>
                    <FormControl>
                        <RadioGroup
                            row
                            aria-labelledby='SidePanel-max-resolution-radio-group-label'
                            value={resolution}
                            name="SidePanel-max-resolution-radio-group"
                            onChange={(event) => {
                                const value = event.target.value

                                dispatch({
                                    type: UPDATE_RESOLUTION,
                                    data: value
                                })
                                sendMessage(webSocket, UPDATE_RESOLUTION, value)
                            }}
                        >
                            <FormControlLabel value="480" control={<Radio size='small'/>} label="480p" />
                            <FormControlLabel value="720" control={<Radio size='small'/>} label="720p" />
                            <FormControlLabel value="1080" control={<Radio size='small'/>} label="1080p" />
                        </RadioGroup>
                    </FormControl>
                </Stack>
            </div>
        </div>
    );
}