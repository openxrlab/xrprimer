import * as React from 'react'
import { useSelector } from 'react-redux'

export default function RenderResContainer(){
    const render_result = useSelector((state) => state.render_result);
    return(
        <>
            {
                render_result && 
                    <div className='RenderResContainer'>
                        <img
                            alt="render_result" 
                            src={render_result}
                            width="100%"
                            height="100%"
                        />
                    </div>
            }
            {
                !render_result && 
                    <div className='RenderResContainer'>
                        <img
                            alt="default_render" 
                            src="../../default_render.png"
                            width="100%"
                            height="100%"
                        />
                    </div>
            }
        </>
    );
}

export { RenderResContainer }