import { Button, Box, Grid } from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import * as React from 'react';
import { useSelector, useDispatch } from 'react-redux';


import {UPDATE_FRAME_INDEX, UPDATE_INSTANT_FRAME, UPDATE_IS_PLAYING} from '../../actions'

export function AnimationPanel(props){

    let isPlaying = useSelector(
        (state) => state.isPlaying
    );

    const frameIndex = useSelector(
        (state) => state.frameIndex
    );

    const frameEnd = useSelector(
        (state) => state.frameEnd
    );

    const dispatch = useDispatch();

    const setPlaying = (isPlaying: Boolean) =>{
        dispatch({
            type: UPDATE_IS_PLAYING,
            data: isPlaying
        })
    };

    return (
        <div className="animation-panel">
            <Box sx={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                <Grid container justifyContent="center" alignItems="center" spacing={2}>
                    <Grid item xs={1}>
                        {
                            isPlaying ? (
                                <Button
                                    className='SidePanel-refresh-page'
                                    variant="outlined"
                                    onClick={() => {
                                        setPlaying(false);
                                    }}
                                >
                                    <PauseIcon />
                                </Button>
                            ) : (
                                <Button
                                    className='SidePanel-refresh-page'
                                    variant="outlined"
                                    onClick={() => {
                                        setPlaying(true);
                                    }}
                                >
                                    <PlayArrowIcon />
                                </Button>
                            )
                        }
                    </Grid>

                    <Grid item xs={3}>
                        <input
                            className="slider"
                            type="range"
                            min={0}
                            max={frameEnd}
                            onChange={(event) => {
                                dispatch({
                                    type: UPDATE_FRAME_INDEX,
                                    data: event.target.value
                                });

                                dispatch({
                                    type: UPDATE_INSTANT_FRAME,
                                    data: true
                                });
                            }}
                            value={frameIndex}
                            step={1}
                        ></input>
                    </Grid>

                    <Grid item xs={3}>
                        <b>{Math.round(frameIndex)}/{Math.round(frameEnd)}</b>
                    </Grid>
                </Grid>
            </Box>

        </div>
    );
}