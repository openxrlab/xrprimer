import {useRef, useEffect} from "react";
import { connect, useDispatch } from "react-redux";
import { Scene, Engine, SceneEventArgs, useScene } from 'react-babylonjs';

import * as BABYLON_GUI from '@babylonjs/gui'
import * as BABYLON from '@babylonjs/core';
import { 
  Color3, Color4, Vector3, Vector4, Matrix, StandardMaterial, ArcRotateCamera, 
  Quaternion, MeshBuilder, HemisphericLight, TransformNode, Viewport, Mesh,
  ActionManager, ExecuteCodeAction
} from "@babylonjs/core";
import { GridMaterial } from "@babylonjs/materials";
import '@babylonjs/loaders';

// TODO: enable vertex streaming
// import { WebSocketContext } from "../WebSocket/WebSocket";
import {
  UPDATE_CAMERA_RELOAD_FLAG, UPDATE_FRAME_INDEX, UPDATE_INSTANT_FRAME, UPDATE_FRAME_END, UPDATE_BODY_RELOAD_FLAG
} from "../../actions";


function disposeSpawnedCameras(scene: BABYLON.Scene, advancedTexture: BABYLON_GUI.AdvancedDynamicTexture){

  const rootNodes = scene.getTransformNodesByTags("spawned_camera");
  rootNodes.forEach((rootNode) => {
    let childNodes = rootNode.getChildren();
    childNodes.forEach((childNode) => {
      let cameraAxes = childNode.getChildren();
      cameraAxes.forEach((cameraAxis) => {
        cameraAxis.dispose();;
      });

      childNode.dispose();
    });
    rootNode.dispose();
  });

  advancedTexture.executeOnAllControls((control) => {
    control.dispose();
  })
}

function UpdateCameraMeshVisibility(scene: BABYLON.Scene, cameraGroupVisibility: Any){
  for(let cameraName in cameraGroupVisibility){
    const visible = cameraGroupVisibility[cameraName]['mesh_visible'];
    const rootNode = scene.getNodeByName(cameraName);

    if(rootNode !== null){
      rootNode.setEnabled(visible);
    }
  }
}

function UpdateCameraLabelVisibility(cameraGroupVisibility: Any, advancedTexture: BABYLON_GUI.AdvancedDynamicTexture){
  for(let cameraName in cameraGroupVisibility){
    const visible = cameraGroupVisibility[cameraName]['label_visible'];
    const controls = advancedTexture.rootContainer.children.filter((child) => {
      return child.name === cameraName;
    });

    if(controls !== null){
      controls.forEach((control) => {
        control.isVisible = visible;
      });
    }
  }
}

async function SpawnCameraInstance(
  idx: Number, 
  scene: BABYLON.Scene,
  cameraParam: Any,
  advancedTexture: BABYLON_GUI.AdvancedDynamicTexture,
  displayCameraLabel: Boolean
){
  const name = String(cameraParam['name']);
  const extrinsic_r = cameraParam['extrinsic_r'];
  const extrinsic_t = cameraParam['extrinsic_t'];
  const convention_type = cameraParam['convention'];

  let rootNode = new BABYLON.TransformNode(name, scene);
  BABYLON.Tags.AddTagsTo(rootNode, "spawned_camera");
  const imported = await BABYLON.SceneLoader.ImportMeshAsync(
    "",
    "../../models/",
    "Camera.glb"
  );
  let meshesRootNode = new BABYLON.TransformNode("meshes_root", scene);
  meshesRootNode.parent = rootNode;
    
  imported.meshes.forEach((mesh) =>{
    // It's possible that the .gltf model being imported might have a non-uniform scaling applied to it,
    // which might cause it to look distorted when assigning a new parent TransformNode to the mesh. 
    // 
    // To solve the issue:
    //  => Decompose the mesh's world matrix to extract the scaling information.
    //  => Reset the mesh's scaling to (1, 1, 1).
    //  => Set the extracted scaling to the parent TransformNode.
    //  => Set the TransformNode as the mesh's parent.
    const scaling = new BABYLON.Vector3();
    const rotation = new BABYLON.Quaternion();
    const position = new BABYLON.Vector3();

    mesh.getWorldMatrix().decompose(scaling, rotation, position);
    mesh.scaling = new BABYLON.Vector3(0.2, 0.2, 0.2);
    meshesRootNode.scaling = scaling;
    mesh.parent = meshesRootNode;
  });

  // create local axes viewer
  let axesRootNode = new BABYLON.TransformNode("axes_root", scene);
  axesRootNode.parent = rootNode;
  const localAxes = new BABYLON.AxesViewer(scene, 0.4);
  localAxes.xAxis.parent = axesRootNode;
  localAxes.yAxis.parent = axesRootNode;
  localAxes.zAxis.parent = axesRootNode;

  // configure camera using uploaded camera params
  let rotation = BABYLON.Matrix.Identity();
  for(let row = 0; row < 3; row++){
    rotation.setRow(
      row, 
      Vector4.FromVector3(Vector3.FromArray(extrinsic_r[row]), 0)
    )
  }

  // transform the rotation from world space back to the camera space
  const rotation_transposed = BABYLON.Matrix.Transpose(rotation);
  rootNode.rotationQuaternion = Quaternion.FromRotationMatrix(rotation_transposed);
  rootNode.position = new Vector3(extrinsic_t[0], extrinsic_t[1], extrinsic_t[2]);

  if(convention_type === "opencv"){
    meshesRootNode.rotation = new Vector3(
      0,
      0,
      BABYLON.Tools.ToRadians(180),
    );
  }

  // create 3d GUI panel for camera info display
  var rect = new BABYLON_GUI.Rectangle();
  rect.width = "400px";
  rect.height = "150px";
  rect.cornerRadius = 10;
  rect.color = "Orange";
  rect.thickness = 2;
  rect.background = "black";
  rect.isVisible = displayCameraLabel;
  rect.name = name;
  advancedTexture.addControl(rect);
  var label = new BABYLON_GUI.TextBlock();
  label.name = name;
  label.text = name;
  label.fontSize = 36;
  const rotation_euler = rootNode.rotationQuaternion.toEulerAngles();
  label.text += "\nT: (" +
    rootNode.position.x.toFixed(2) + ", " +
    rootNode.position.y.toFixed(2) + ", " +
    rootNode.position.z.toFixed(2) + ")";
  label.text += "\nR: (" + 
    BABYLON.Tools.ToDegrees(rotation_euler.x).toFixed(1) + ", " +
    BABYLON.Tools.ToDegrees(rotation_euler.y).toFixed(1) + ", " +
    BABYLON.Tools.ToDegrees(rotation_euler.z).toFixed(1) + ")";
  rect.addControl(label);
  rect.linkWithMesh(meshesRootNode);
  rect.linkOffsetY = -300;  

  var target = new BABYLON_GUI.Ellipse();
  target.name = name;
  target.width = "20px";
  target.height = "20px";
  target.color = "Orange";
  target.thickness = 4;
  target.background = "green";
  advancedTexture.addControl(target);
  target.linkWithMesh(meshesRootNode);
  target.isVisible = displayCameraLabel;

  var line = new BABYLON_GUI.Line();
  line.name = name;
  line.lineWidth = 4;
  line.color = "Orange";
  line.y2 = 75;
  line.linkOffsetY = -10;
  advancedTexture.addControl(line);
  line.linkWithMesh(meshesRootNode);
  line.connectedControl = rect;
  line.isVisible = displayCameraLabel;
}

export type CustomedCameraMeshesProps = {
  cameraReloadFlag: Any,
  cameraParams: Any,
  advancedTexture: BABYLON_GUI.AdvancedDynamicTexture,
  displayCameraLabel: Boolean,
  dispatch: Any
};

function CustomedCameraMeshes(props: CustomedCameraMeshesProps){
  const cameraReloadFlag = props.cameraReloadFlag;
  const cameraParams = props.cameraParams;
  const advancedTexture = props.advancedTexture;
  const displayCameraLabel = props.displayCameraLabel;
  const cameraGroupVisibility = props.cameraGroupVisibility;
  const dispatch = props.dispatch;
  const scene = useScene();

  useEffect(() => {
    if(advancedTexture){
      const _cameraGroupVisibility = JSON.parse(cameraGroupVisibility);
      UpdateCameraLabelVisibility(_cameraGroupVisibility, advancedTexture);
      UpdateCameraMeshVisibility(scene, _cameraGroupVisibility);
    }
  }, [scene, advancedTexture, cameraGroupVisibility]);

  useEffect(() => {  
    if(scene){
      const onBeforeRender = () => {
        if(cameraReloadFlag === true){
          disposeSpawnedCameras(scene, advancedTexture);
          for(let idx = 0; idx < cameraParams.length; idx++){
            SpawnCameraInstance(idx, scene, cameraParams[idx], advancedTexture, displayCameraLabel);
          }
          dispatch({
            type: UPDATE_CAMERA_RELOAD_FLAG,
            data: false
          });
        }
      }
      scene.registerBeforeRender(onBeforeRender);

      return () => {
        scene.unregisterBeforeRender(onBeforeRender);
      }
    }
  }, [scene, cameraReloadFlag, cameraParams, displayCameraLabel, advancedTexture, dispatch]);

  return(
    <>
    </>
  );
}

export type CustomedBodyMeshesProps = {
  bodyReloadFlag: Boolean,
  assetsManager: BABYLON.AssetsManager,
  bodyMotion: Str,
  isPlaying: Boolean,
  frameIndex: Number,
  instantFrame: Boolean,
  onUpdateInstantFrame: Function,
  dispatch: Any
};

function CustomedBodyMeshes(props: CustomedBodyMeshesProps){
  const bodyReloadFlag = props.bodyReloadFlag;
  const bodyMotion = props.bodyMotion;
  const assetsManager = props.assetsManager;
  const isPlaying = props.isPlaying;
  const frameIndex = props.frameIndex;
  const instantFrame = props.instantFrame;
  const dispatch = props.dispatch;
  const scene = useScene();
  const bodyMeshRef = useRef(null);
  const bodyAnimationRef = useRef(null);

  const getCurrentFrame = (animationGroup: BABYLON.AnimationGroup) => {
    if(!animationGroup){
      return 0;
    }

    const targetedAnimations = animationGroup.targetedAnimations;
    if(targetedAnimations.length > 0){
      const runtimeAnimations = targetedAnimations[0].animation.runtimeAnimations;
      if(runtimeAnimations.length > 0){
        return runtimeAnimations[0].currentFrame;
      }
    }

    return 0;
  }

  useEffect(() => {
    if(scene){
      const onBeforeRender = () => {
        if(bodyReloadFlag){
          if(bodyMeshRef.current !== null){
            // Clear the existing character animation before importing a new animtion.
            // Notice that Babylon.js will release all resources associated with the 
            // mesh, including any textures, materials, and animations.
            bodyMeshRef.current.dispose();
          }
          
          // BUG: if the filename is in upper case, the assets manager fails to parse motion file
          let meshTask = assetsManager.addMeshTask("task", "", "file:", bodyMotion);
          assetsManager.loadAsync();

          meshTask.onSuccess = (task) => {
            let bodyMesh = task.loadedMeshes[0];
            let bodyAnimation = task.loadedAnimationGroups[0];
            
            bodyMeshRef.current = bodyMesh;
            bodyAnimationRef.current = bodyAnimation;
            
            dispatch({
              type: UPDATE_FRAME_END,
              data: bodyAnimation.to
            });
          };
          
          meshTask.onError = (task, message, exception) => {
            console.log(message);
            console.log(exception);
          }
          dispatch({
            type: UPDATE_BODY_RELOAD_FLAG,
            data: false
          });
        }

        if(bodyAnimationRef.current !== null){
          if(isPlaying){
            const currentFrameIndex = getCurrentFrame(bodyAnimationRef.current);

            dispatch({
              type: UPDATE_FRAME_INDEX,
              data: currentFrameIndex
            });

            if(bodyAnimationRef.current.isPlaying === false){
              bodyAnimationRef.current.play();
            }
          }
          else{
            if(bodyAnimationRef.current.isPlaying === true){
              bodyAnimationRef.current.pause();
            }      
          }

          if(instantFrame){
            bodyAnimationRef.current.goToFrame(frameIndex);

            dispatch({
              type: UPDATE_INSTANT_FRAME,
              data: false
            });
          }
        }
      }
      scene.registerBeforeRender(onBeforeRender);

      return () => {
        scene.unregisterBeforeRender(onBeforeRender);
      }
    }
  }, [scene, bodyReloadFlag, isPlaying, frameIndex, assetsManager, bodyMotion, instantFrame, dispatch]);

  return(
    <>
    </>
  );
}

function SpawnGround(scene: BABYLON.Scene){
  const ground = MeshBuilder.CreateGround(
    "ground",
    {width: 100, height: 100},
    scene
  )
  ground.position = new Vector3(0, 0, 0);
  ground.rotate(new Vector3(1, 0, 0), BABYLON.Tools.ToRadians(180));
  const groundMat = new GridMaterial(
    "groundMaterial",
    scene
  );
  groundMat.majorUnitFrequency = 5;
  groundMat.minorUnitVisibility = 0.5;
  
  groundMat.gridRatio = 2;
  groundMat.opacity = 0.999;
  groundMat.useMaxLine = true;
  groundMat.lineColor = new Color3(1, 1, 1);
  groundMat.mainColor = new Color3(1, 1, 1);
  groundMat.backFaceCulling = false;

  ground.material = groundMat;
}

function SpawnLight(scene: BABYLON.Scene){
  const hemiLight = new HemisphericLight(
    "hemiLight",
    new Vector3(0, -1, 0),
    scene
  );
  hemiLight.intensity = 0.95;
}

function SpawnEnvTex(scene: BABYLON.Scene){
  const envTex = BABYLON.CubeTexture.CreateFromPrefilteredData(
    "../../environment/pizzo_pernice_puresky.env", 
    scene
  );
  let reflectionMatrix = Matrix.Identity();
  Quaternion.FromEulerVector(new Vector3(-Math.PI, 0, 0)).toRotationMatrix(reflectionMatrix);
  envTex.setReflectionTextureMatrix(reflectionMatrix);
  scene.environmentTexture = envTex;
  scene.createDefaultSkybox(envTex, true);
  scene.environmentIntensity = 0.9;
}

function SpawnCamera(engine: BABYLON.Engine, scene: BABYLON.Scene){
      // *********************** spawn roaming camera ***********************
    // the HUD camera must share the same configurations with the roaming camera
    const panningSensibility = 2000;
    const angularSensibilityX = 2000;
    const angularSensibilityY = 2000;
    const alpha = BABYLON.Tools.ToRadians(75);
    const beta = BABYLON.Tools.ToRadians(240);

    const camera = new ArcRotateCamera(
      "camera",
      alpha,
      beta,
      3,
      Vector3.Zero(),
      scene
    );

    camera.attachControl();
    camera.fov = BABYLON.Tools.ToRadians(60);
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
    camera.upperBetaLimit = 180;
    camera.lowerBetaLimit = -180;
    // enable keyboard control of camera
    // see https://www.toptal.com/developers/keycode for keycode.
    camera.keysUp.push(87);
    camera.keysDown.push(83);
    camera.keysLeft.push(65);
    camera.keysRight.push(68);

    let translation = Vector3.Zero();
    let rotation = Quaternion.Zero();

    function get_camera_translation_and_rotation(camera: BABYLON.Camera){
      let cameraWorldMatrix = camera.getWorldMatrix();
      let cameraViewMatrix = camera.getViewMatrix();
      cameraWorldMatrix.decompose(null, null, translation);
      cameraViewMatrix.decompose(null, rotation, null);
      const rotMat = Matrix.Zero();
      rotation.toRotationMatrix(rotMat);
      
      return [translation, rotMat]
    }

    const cameraTransXDiv = document.getElementById('cameraTransX');
    const cameraTransYDiv = document.getElementById('cameraTransY');
    const cameraTransZDiv = document.getElementById('cameraTransZ');
    const cameraRotationXDiv = document.getElementById('cameraRotationX');
    const cameraRotationYDiv = document.getElementById('cameraRotationY');
    const cameraRotationZDiv = document.getElementById('cameraRotationZ');

    camera.onViewMatrixChangedObservable.add(() => {
      let [camera_translation, camera_roation] = get_camera_translation_and_rotation(camera);
      let cameraEulerRotationRadians = Quaternion.FromRotationMatrix(camera_roation).toEulerAngles();
      let cameraEulerRotationDegrees = new BABYLON.Vector3(
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.x),
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.y),
        BABYLON.Tools.ToDegrees(cameraEulerRotationRadians.z)
      );

      cameraTransXDiv.innerText = camera_translation.x.toFixed(2);
      cameraTransYDiv.innerText = camera_translation.y.toFixed(2);
      cameraTransZDiv.innerText = camera_translation.z.toFixed(2);
      cameraRotationXDiv.innerText = cameraEulerRotationDegrees.x.toFixed(2);
      cameraRotationYDiv.innerText = cameraEulerRotationDegrees.y.toFixed(2);
      cameraRotationZDiv.innerText = cameraEulerRotationDegrees.z.toFixed(2);

      camera_translation = camera_translation.asArray();
      camera_roation = Array.from(Matrix.GetAsMatrix3x3(camera_roation));
    });

    // *********************** spawn roaming camera ***********************

    // *********************** spawn HUD camera ***********************
    const cameraHUD = new ArcRotateCamera(
      "cameraHUD",
      alpha,
      beta,
      3,
      Vector3.Zero(),
      scene
    );
    // cameraHUD.position = position;
    cameraHUD.attachControl();
    cameraHUD.lowerRadiusLimit = 0.1;
    cameraHUD.layerMask = 0x20000000;
    cameraHUD.viewport = new Viewport(0.90, 0.85, 0.12, 0.17);
    cameraHUD.panningSensibility = panningSensibility;
    cameraHUD.angularSensibilityX = angularSensibilityX;
    cameraHUD.angularSensibilityY = angularSensibilityY;

    cameraHUD.upperBetaLimit = 180;
    cameraHUD.lowerBetaLimit = -180;

    scene.activeCameras = [camera, cameraHUD];  // HUD camera must be the last // must be last?
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

    // Update Axes position to be in the center of the screen without perspective distortion
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
}

function HandleWindowResize(canvas: HTMLCanvasElement){
    const canvasSizeXDiv = document.getElementById('canvasSizeX');
    const canvasSizeYDiv = document.getElementById('canvasSizeY');
    canvasSizeXDiv.innerText = canvas.width.toFixed(0);
    canvasSizeYDiv.innerText = canvas.height.toFixed(0);

    function callback(){
      canvasSizeXDiv.innerText = canvas.width.toFixed(0);
      canvasSizeYDiv.innerText = canvas.height.toFixed(0);
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
}

function ViewerWindow(props){
  const {
    cameraReloadFlag, cameraParams, bodyMotion, bodyReloadFlag, isPlaying, frameIndex, instantFrame, displayCameraLabel, cameraGroupVisibility,
  } = props;

  // TODO: enable vertex streaming
  // const webSocket = useContext(WebSocketContext).socket;
  const sceneRef = useRef(null);
  const assetManagerRef = useRef(null);
  const advancedTextureRef = useRef(null);
  const dispatch = useDispatch();

  const onSceneMount = (e: SceneEventArgs) => {
    const { canvas, scene } = e;
    const engine = scene.getEngine();

    scene.useRightHandedSystem = true;
    sceneRef.current = scene;

    SpawnGround(scene);
    SpawnLight(scene);
    SpawnEnvTex(scene);
    SpawnCamera(engine, scene);
    HandleWindowResize(canvas);
    
    let assetsManager = new BABYLON.AssetsManager(scene);  
    assetManagerRef.current = assetsManager;

    let advancedTexture = BABYLON_GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
    advancedTextureRef.current = advancedTexture;

    // *********************** render loop ***********************
    engine.runRenderLoop(() => {
      if(scene){
        const fpsDiv = document.getElementById('fpsDiv');
        fpsDiv.innerText = engine.getFps().toFixed() + "fps";
      }
    });
    // *********************** render loop ***********************
  }

  return (
    <>
      <div className="canvas-container">
        <Engine antialias adaptToDeviceRatio canvasId="babylon-canvas">
          <Scene
            clearColor={new Color4(0, 0, 0, 0.4)}
            onSceneMount={onSceneMount}
          >
            <CustomedCameraMeshes
              cameraParams={cameraParams}
              cameraReloadFlag={cameraReloadFlag}
              advancedTexture={advancedTextureRef.current}
              displayCameraLabel={displayCameraLabel}
              cameraGroupVisibility={cameraGroupVisibility}
              dispatch={dispatch}
            />
            <CustomedBodyMeshes
              bodyReloadFlag={bodyReloadFlag}
              assetsManager={assetManagerRef.current}
              bodyMotion={bodyMotion}
              isPlaying={isPlaying}
              frameIndex={frameIndex}
              instantFrame={instantFrame}
              dispatch={dispatch}
            />
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
    cameraParams: state.cameraParams,
    cameraReloadFlag: state.cameraReloadFlag,
    bodyMotion: state.bodyMotion,
    bodyReloadFlag: state.bodyReloadFlag,
    isPlaying: state.isPlaying,
    frameIndex: state.frameIndex,
    instantFrame: state.instantFrame,
    displayCameraLabel: state.displayCameraLabel,
    cameraGroupVisibility: state.cameraGroupVisibility
  }
}

const ViewerWindowConnected = connect(
  mapStateToProps,
  mapDispatchToProps
)(ViewerWindow)

export default ViewerWindowConnected;