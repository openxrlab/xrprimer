import React from 'react';

import Button from '@mui/material/Button'
import GithubIcon from '@mui/icons-material/GitHub'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionRounded';
// import CollectionsOutlinedIcon from '@mui/icons-material/CollectionsOutlined';

export default function Banner(){
    return(
        <div className='banner'>
            <Button 
                className="banner-button"
                variant="outlined"
                startIcon={<DescriptionOutlinedIcon/>}
                target="_blank"
                href="https://www.google.com"
                size="small"
            >
                Documentation   
            </Button>

            <Button
                className="banner-button"
                variant="outlined"
                startIcon={<GithubIcon/>}
                target="_blank"
                href="https://www.github.com"
                size="small"
            >
                Github
            </Button>
        
            <div className='banner-logo'>
                <img
                    style={{height:30, margin: 'auto'}}
                    src="./OpenXRLab-logo.png"
                    alt="logo"
                />
            </div>

        </div>
    );
}