import {useContext, useRef} from "react";
import { connect } from "react-redux";
import { Scene, Engine, SceneEventArgs} from 'react-babylonjs';
import { 
  Color3, Color4, Vector3, Matrix, StandardMaterial, ArcRotateCamera, Quaternion, Mesh, MeshBuilder,
  HemisphericLight, TransformNode, Viewport, ActionManager, ExecuteCodeAction
} from "@babylonjs/core";
import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders';
import { GridMaterial } from "@babylonjs/materials";
import { RenderResContainer } from "../RenderResContainer/RenderResContainer";
import { WebSocketContext } from "../WebSocket/WebSocket";
import {
  sendMessage,
  UPDATE_CAMERA_TRANSLATION, UPDATE_CAMERA_ROTATION, UPDATE_CAMERA_FOV, UPDATE_RENDER_TYPE, UPDATE_RESOLUTION
} from "../../actions";

function ViewerWindow(props){
  const {
    cameraFOV, renderType, resolution,
  } = props;
  const webSocket = useContext(WebSocketContext).socket;
  const cameraRef = useRef(null);

  const onSceneMount = (e: SceneEventArgs) => {
    const { canvas, scene } = e;
    const engine = scene.getEngine();

    scene.useRightHandedSystem = true;

    // *********************** spawn ground ***********************
    const ground = MeshBuilder.CreateGround(
      "ground",
      {width: 100, height: 100},
      scene
    )
    ground.position = new Vector3(0, 0, 0);

    const groundMat = new GridMaterial(
      "groundMaterial",
      scene
    );
    groundMat.majorUnitFrequency = 5;
    groundMat.minorUnitVisibility = 0.3;
    groundMat.gridRatio = 2;
    groundMat.opacity = 0.99;
    groundMat.useMaxLine = true;
    groundMat.lineColor = new Color3(0, 0, 0);
    groundMat.mainColor = new Color3(0, 0, 0);
    groundMat.backFaceCulling = false;

    ground.material = groundMat;
    // *********************** spawn ground ***********************
    
    // *********************** spawn light ***********************
    const hemiLight = new HemisphericLight(
      "hemiLight",
      new Vector3(0, 1, 0),
      scene
    );
    hemiLight.intensity = 0.95;
    // *********************** spawn light ***********************

    // *********************** handle window resize ***********************
    const canvasSizeXDiv = document.getElementById('canvasSizeX');
    const canvasSizeYDiv = document.getElementById('canvasSizeY');
    canvasSizeXDiv.innerText = canvas.width.toFixed(0);
    canvasSizeYDiv.innerText = canvas.height.toFixed(0);
    // onUpdateCanvasSize([canvas.width, canvas.height]);

    function callback(){
      const width = canvas.width;
      const height = canvas.height;
      // onUpdateCanvasSize([width, height]);
      canvasSizeXDiv.innerText = width.toFixed(0);
      canvasSizeYDiv.innerText = height.toFixed(0);
    }

    function setResizeHandler(callback, timeout){
      let timer_id = undefined;
      window.addEventListener("resize", function(){
        if(timer_id !== undefined){
          clearTimeout(timer_id);
          timer_id = undefined;
        }
        timer_id = setTimeout(function(){
          timer_id = undefined;
          callback();
        }, timeout)
      });
    }

    setResizeHandler(callback, 0);
    // *********************** handle window resize ***********************

    // *********************** spawn roaming camera ***********************

    // the HUD camera must share the same sensibility configurations with the roaming camera
    const panningSensibility = 2000;
    const angularSensibilityX = 2000;
    const angularSensibilityY = 2000;

    const camera = new ArcRotateCamera(
      "camera",
      -Math.PI / 3, 
      Math.PI / 3, 
      10,
      Vector3.Zero(),
      scene
    );
    camera.attachControl();
    camera.fov = BABYLON.Tools.ToRadians(cameraFOV);
    camera.panningSensibility = panningSensibility;
    camera.angularSensibilityX = angularSensibilityX;
    camera.angularSensibilityY = angularSensibilityY;
    camera.maxZ = 999;
    camera.minZ = 0;
    camera.wheelPrecision = 50;
    // prevent camera from infinite zoom in
    // see https://doc.babylonjs.com/features/featuresDeepDive/behaviors/cameraBehaviors
    camera.lowerRadiusLimit = 0.1;
    camera.useBouncingBehavior = true;
    
    // enable keyboard control of camera
    // see https://www.toptal.com/developers/keycode for keycode.
    camera.keysUp.push(87);
    camera.keysDown.push(83);
    camera.keysLeft.push(65);
    camera.keysRight.push(68);

    cameraRef.current = camera;

    let translation = Vector3.Zero();
    let rotation = Quaternion.Zero();

    function get_camera_translation_and_rotation(camera: BABYLON.Camera){
      let cameraWorldMatrix = camera.getWorldMatrix();
      let cameraViewMatrix = camera.getViewMatrix();
      cameraWorldMatrix.decompose(null, null, translation);
      cameraViewMatrix.decompose(null, rotation, null);
      const rotMat = Matrix.Zero();
      rotation.toRotationMatrix(rotMat);
      
      return {
        trans_vec: translation,
        rot_mat: rotMat
      }
    }

    const cameraTransXDiv = document.getElementById('cameraTransX');
    const cameraTransYDiv = document.getElementById('cameraTransY');
    const cameraTransZDiv = document.getElementById('cameraTransZ');
    const cameraRotationXDiv = document.getElementById('cameraRotationX');
    const cameraRotationYDiv = document.getElementById('cameraRotationY');
    const cameraRotationZDiv = document.getElementById('cameraRotationZ');

    camera.onViewMatrixChangedObservable.add(() => {
      let camera_extrinsic = get_camera_translation_and_rotation(camera);
      let camera_translation = camera_extrinsic.trans_vec;
      let camera_rotation = camera_extrinsic.rot_mat;
      let cameraEulerRotationRadians = Quaternion.FromRotationMatrix(camera_rotation).toEulerAngles();
      let cameraEulerRotationDegrees = new BABYLON.Vector3(
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.x),
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.y),
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.z)
      );
      
      // set side panel camera extrinsic display
      cameraTransXDiv.innerText = camera_translation.x.toFixed(2);
      cameraTransYDiv.innerText = camera_translation.y.toFixed(2);
      cameraTransZDiv.innerText = camera_translation.z.toFixed(2);
      cameraRotationXDiv.innerText = cameraEulerRotationDegrees.x.toFixed(2);
      cameraRotationYDiv.innerText = cameraEulerRotationDegrees.y.toFixed(2);
      cameraRotationZDiv.innerText = cameraEulerRotationDegrees.z.toFixed(2);
      
      // send camera extrinsic to bridge server
      let trans_arr = camera_translation.asArray();
      let rot_arr = Array.from(Matrix.GetAsMatrix3x3(camera_rotation));
      // onUpdateCameraTranslation(trans_arr);
      // onUpdateCameraRotation(rot_arr);
      sendMessage(webSocket, UPDATE_CAMERA_TRANSLATION, trans_arr);
      sendMessage(webSocket, UPDATE_CAMERA_ROTATION, rot_arr);
    });

    camera.onProjectionMatrixChangedObservable.add(() => {
      camera.fov = BABYLON.Tools.ToRadians(cameraFOV);
    });
    // *********************** spawn roaming camera ***********************

    // *********************** spawn HUD camera ***********************
    const cameraHUD = new ArcRotateCamera(
      "cameraHUD",
      -Math.PI / 3, 
      Math.PI / 3, 
      10,
      Vector3.Zero(),
      scene
    );

    cameraHUD.attachControl();
    cameraHUD.lowerRadiusLimit = 0.1;
    cameraHUD.layerMask = 0x20000000;
    cameraHUD.viewport = new Viewport(0.90, 0.85, 0.12, 0.17);
    cameraHUD.panningSensibility = panningSensibility;
    cameraHUD.angularSensibilityX = angularSensibilityX;
    cameraHUD.angularSensibilityY = angularSensibilityY;
    
    scene.activeCameras = [camera, cameraHUD];  // HUD camera must be the last
    // *********************** spawn HUD camera ***********************
    
    // register camera pointer event
    scene.onPointerObservable.add((eventData) => {
      let rect = engine.getRenderingCanvasClientRect();
      let x = eventData.event.clientX - rect.left;
      let y = eventData.event.clientY - rect.top;

      if (x >= (rect.width * 0.90) && y <= (rect.height * 0.15)){
        scene.cameraToUseForPointers = cameraHUD;
      }
      else {
        scene.cameraToUseForPointers = camera;
      }
    }, BABYLON.PointerEventTypes.POINTERMOVE);

    // *********************** spawn axes ***********************
    const instance = new TransformNode('axes', scene);
    const size = 1;
    const origin = Vector3.Zero();
    const dot = MeshBuilder.CreateSphere('hover', {diameter: size / 2, segments: 4}, scene);
    const mat = new StandardMaterial('mat', scene);
    mat.disableLighting = true;
    mat.emissiveColor = Color3.White();
    dot.material = mat;
    dot.renderingGroupId = 1;
    dot.layerMask = 0x20000000;
    dot.setEnabled(false);
    dot.parent = instance;
 
    function createAxis(name: string, color: Color3, sign: Number = 1, addLabel: Boolean= false){
      const mat = new StandardMaterial(name, scene);
      mat.checkReadyOnlyOnce = true;
      mat.disableLighting = true;
      mat.emissiveColor = color;
      
      if(sign < 0){   // negative axis
        mat.alpha = 0.3;
        mat.alphaMode = BABYLON.Engine.ALPHA_COMBINE;
      }
      let mesh = MeshBuilder.CreateSphere(name, {diameter: size, segments: 8}, scene);

      if(sign > 0){
        const pos = origin.clone();
        pos[name] = -sign * size * 2;
        const tube = MeshBuilder.CreateTube(
          'tube', 
          {path: [pos, origin], radius: sign / 10, cap: 1, tessellation: 6}, 
          scene
        );
        tube.material = mat;
        mesh = Mesh.MergeMeshes([mesh, tube], true);
      }
      mesh.position[name] = sign * size * 2;
      mesh.layerMask = 0x20000000;
      mesh.material = mat;
      mesh.parent = instance;
      mesh.id = `${sign < 0 ? '-' : ''}${name}`;

      // interaction
      const actionManager = mesh.actionManager = new ActionManager(scene);
      actionManager.registerAction(
        new ExecuteCodeAction(
          ActionManager.OnPointerOverTrigger,
          ({meshUnderPointer}) => {
            console.log("over trigger");
            dot.position = meshUnderPointer.position;
            dot.setEnabled(true);
          }
        )
      );
      actionManager.registerAction(
        new ExecuteCodeAction(
          ActionManager.OnPointerOutTrigger,
          ({meshUnderPointer}) => {
            console.log("out trigger");
            dot.setEnabled(false);
          }
        )
      );
      actionManager.registerAction(
        new ExecuteCodeAction(
          ActionManager.OnLeftPickTrigger,
          ({meshUnderPointer}) => {
            setCameraAngle(meshUnderPointer.id);
          }
        )
      );

      actionManager.hoverCursor = 'pointer';

      return mesh;
    }

    const red   = new Color3(1.00, 0.10, 0.30);
    const green = new Color3(0.30, 0.65, 0.10);
    const blue  = new Color3(0.10, 0.50, 0.90);
    
    createAxis('x', red,   1, true);
    createAxis('x', red,   -1     );
    createAxis('y', green, 1, true);
    createAxis('y', green, -1     );
    createAxis('z', blue,  1, true);
    createAxis('z', blue,  -1     );

    scene.onBeforeCameraRenderObservable.add(() => {
      instance.position = cameraHUD.getFrontPosition(size * 10);
    });

    function setCameraAngle(id) {
      switch(id) {
        case 'x':
          camera.alpha = cameraHUD.alpha = 0;
          camera.beta  = cameraHUD.beta  = Math.PI / 2;
          return;
        case '-x':
          camera.alpha = cameraHUD.alpha = -Math.PI;
          camera.beta  = cameraHUD.beta  = Math.PI / 2;
          return;
        case 'y':
          camera.alpha = cameraHUD.alpha = -Math.PI / 2;
          camera.beta  = cameraHUD.beta  = 0;
          return;
        case '-y':
          camera.alpha = cameraHUD.alpha = -Math.PI / 2;
          camera.beta  = cameraHUD.beta  = Math.PI;
          return;
        case 'z':
          camera.alpha = cameraHUD.alpha = Math.PI / 2;
          camera.beta  = cameraHUD.beta  = Math.PI / 2;
          return;
        case '-z':
          camera.alpha = cameraHUD.alpha = -Math.PI / 2;
          camera.beta  = cameraHUD.beta  = Math.PI / 2;
          return;
        default:
          return;
      }
    }

    // *********************** spawn axes ***********************

    // *********************** render loop ***********************
    let bInitialStateSent = false;

    engine.runRenderLoop(() => {
      if(scene){
        if(bInitialStateSent === false){
          let camera_extrinsic = get_camera_translation_and_rotation(camera);
          let trans_arr = camera_extrinsic.trans_vec.asArray();
          let rot_arr = Array.from(Matrix.GetAsMatrix3x3(camera_extrinsic.rot_mat));

          let bSent = sendMessage(webSocket, UPDATE_CAMERA_TRANSLATION, trans_arr);
          sendMessage(webSocket, UPDATE_CAMERA_ROTATION, rot_arr);
          sendMessage(webSocket, UPDATE_CAMERA_FOV, cameraFOV);
          sendMessage(webSocket, UPDATE_RENDER_TYPE, renderType);
          sendMessage(webSocket, UPDATE_RESOLUTION, resolution);

          // make sure the camera params are successfully sent to the backend
          if(bSent){
            bInitialStateSent = true;
          }
        }

        const fpsDiv = document.getElementById('fpsDiv');
        fpsDiv.innerText = engine.getFps().toFixed() + "fps";
      }
    });
    // *********************** render loop ***********************
  }

  const onBeforeRenderObservable = () => {
    if(cameraRef !== null){
      cameraRef.current.fov = BABYLON.Tools.ToRadians(cameraFOV);
    }
  }

  return (
    <>
      <RenderResContainer />
      <div className="canvas-container">
        <Engine antialias adaptToDeviceRatio canvasId="babylon-canvas">
          <Scene
            clearColor={new Color4(0, 0, 0, 0.4)}
            onSceneMount={onSceneMount}
            onBeforeRenderObservable={onBeforeRenderObservable}
          >
          </Scene>
        </Engine>
      </div>
    </>
  );
}

const mapDispatchToProps = (dispatch) => {
  return {
  }
}

const mapStateToProps = (state) => {
  return {
    cameraTranslation: state.cameraTranslation,
    cameraRotation: state.cameraRotation,
    cameraFOV: state.cameraFOV,
    renderType: state.renderType,
    resolution: state.resolution,
    canvasSize: state.canvasSize,
  }
}

const ViewerWindowConnected = connect(
  mapStateToProps,
  mapDispatchToProps
)(ViewerWindow)

export default ViewerWindowConnected;