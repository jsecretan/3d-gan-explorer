import * as React from "react";
import * as BABYLON from "babylonjs";
import 'babylonjs-loaders';
import BabylonScene, { SceneEventArgs } from "./SceneComponent";

class PageWithScene extends React.Component<{}, {}> {
  onSceneMount = (e: SceneEventArgs) => {
    const { canvas, scene, engine } = e;

        // This creates and positions a free camera (non-mesh)
        //const camera = new BABYLON.FreeCamera("camera1", new BABYLON.Vector3(0, 5, -10), scene);
        var camera = new BABYLON.UniversalCamera("UniversalCamera", new BABYLON.Vector3(0, 0, -10), scene);

        // This targets the camera to scene origin
        //camera.setTarget(BABYLON.Vector3.Zero());

        // This attaches the camera to the canvas
        camera.attachControl(canvas, true);

        // This creates a light, aiming 0,1,0 - to the sky (non-mesh)
        const light = new BABYLON.HemisphericLight("light1", new BABYLON.Vector3(0, 1, 0), scene);

        // Default intensity is 1. Let's dim the light a small amount
        light.intensity = 0.7;

        //When click event is raised
        window.addEventListener("click", function (evt) {
           // We try to pick an object
           var pickResult = scene.pick(evt.clientX, evt.clientY);
           if(pickResult.hit) {
            console.log(pickResult.pickedMesh)
           }
        });

        // Makes a white plastic kind of look that matches my default 3d printer material
        var myMaterial = new BABYLON.StandardMaterial("myMaterial", scene);
        myMaterial.diffuseColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.emissiveColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.ambientColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.backFaceCulling = false;
        myMaterial.alpha = 1;

        var spacing = 10.0;
        var x0 = -6.0;
        var y0 = -6.0;
        var meshCount = 0;
        var angles = new Array(10);
        angles.fill(0.01);

        for(var i = 0; i < 9; i++) {
            BABYLON.SceneLoader.ImportMesh("", "http://192.168.86.73:5000/generate/", Math.random()+".obj", scene, function (newMeshes) {
                newMeshes[0].material = myMaterial;
                newMeshes[0].position.x = x0+(meshCount%3)*spacing;
                newMeshes[0].position.y = y0+Math.floor(meshCount/3)*spacing;
                newMeshes[0].position.z = 5.0;
                newMeshes[0].rotate(BABYLON.Axis.X, -90.0, BABYLON.Space.WORLD);
                newMeshes[0].createNormals(true);

                // Spin the models right round so you can see all of them
                scene.registerBeforeRender(function() {
                    newMeshes[0].rotate(BABYLON.Axis.Y, angles[meshCount], BABYLON.Space.WORLD);
                });

                meshCount = meshCount + 1;

            });
        }

    engine.runRenderLoop(() => {
      if (scene) {
        scene.render();
      }
    });
  };

  render() {
    return (
      <div>
        <BabylonScene
          width={1000}
          height={700}
          onSceneMount={this.onSceneMount}
        />
      </div>
    );
  }
}

export default PageWithScene;
