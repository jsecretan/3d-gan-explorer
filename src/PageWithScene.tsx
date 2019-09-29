import * as React from "react";
import * as BABYLON from "babylonjs";
import 'babylonjs-loaders';
import BabylonScene, { SceneEventArgs } from "./SceneComponent";
import 'babylonjs-serializers';
//import 'lodash.product';
const lodash = require("lodash.product");
let _ = require('lodash');

//import * as hilbertCurve from "hilbert-curve";
//import 'hilbert-curve';
const hilbertCurve = require("hilbert-curve");

// function loadAllInView(position) {

// }

class PageWithScene extends React.Component<{}, {}> {

  loadedMeshes: Set<number> = new Set<number>();

  squareToIndex(square: Array<number>): number {
    return hilbertCurve.pointToIndex({ x: square[0], y: square[1]}, 1000);
  }

    loadMesh(square: Array<number>, scene: BABYLON.Scene) {

                // Makes a white plastic kind of look that matches my default 3d printer material
        var myMaterial = new BABYLON.StandardMaterial("myMaterial", scene);
        myMaterial.diffuseColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.emissiveColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.ambientColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        myMaterial.backFaceCulling = false;
        myMaterial.alpha = 1;

        var angle = 0.01;

            console.log("Running the mesh load");

        BABYLON.SceneLoader.ImportMesh("", "http://192.168.86.247:5000/generate/", ((this.squareToIndex(square)/1e6)+0.01)+'.obj', scene, function (newMeshes) {
            newMeshes[0].material = myMaterial;
            newMeshes[0].position.x = square[0]
            newMeshes[0].position.y = square[1]
            newMeshes[0].position.z = 5.0;
            newMeshes[0].rotate(BABYLON.Axis.X, -90.0, BABYLON.Space.WORLD);
            newMeshes[0].createNormals(true);



            // Spin the models right round so you can see all of them
            scene.registerBeforeRender(function() {
                newMeshes[0].rotate(BABYLON.Axis.Y, angle, BABYLON.Space.WORLD);
            });

        });
    }


    load_all_in_view(x: number, y: number, scene: BABYLON.Scene): void {

        var spacing = 10.0;

        // Turn the current rectangle into which grids it represents
        var x_values = [];
        for (var i = Math.floor((x-20.0)/spacing); i <= Math.floor((x+20.0)/spacing)+1; i++) {
            x_values.push(spacing * i);
        }

        var y_values = [];
        for (i = Math.floor((y-20.0)/spacing); i <= Math.floor((y+20.0)/spacing)+1; i++) {
            y_values.push(spacing * i);
        }

        var view_grids = _.product(x_values, y_values);


        // See if there is any empty grid space that we need to fill with generated objects
        for(var square of view_grids) {

            if(this.loadedMeshes.has(this.squareToIndex(square)) === false) {
                console.log("Loading model for square: " + square);
                this.loadMesh(square, scene);
                // Make sure to mark this as loaded
                this.loadedMeshes.add(this.squareToIndex(square));
            

            }


        }

    }

  onSceneMount = (e: SceneEventArgs) => {
    const { canvas, scene, engine } = e;

        // Got the snippet from here: https://playground.babylonjs.com/#K9MWF6#3
        var camera = new BABYLON.ArcRotateCamera('camera', -Math.PI / 2, Math.PI / 2, 10, new BABYLON.Vector3(0, 0, -10), scene);
        camera.attachControl(canvas, true, false, 1);
        camera.attachControl(canvas, true, false);
        camera.panningAxis = new BABYLON.Vector3(1, 1, 0);
        camera.upperBetaLimit = Math.PI / 2;
        camera.wheelPrecision = 1;
        camera.panningSensibility = 100;
        camera.inertia = 0.1;
        camera.panningInertia = 0.8;
        camera._panningMouseButton = 0; // change functionality from left to right mouse button
        camera.angularSensibilityX = 500;

        camera.angularSensibilityY = 500;

        // This creates a light, aiming 0,1,0 - to the sky (non-mesh)
        const light = new BABYLON.HemisphericLight("light1", new BABYLON.Vector3(0, 1, 0), scene);

        // Default intensity is 1. Let's dim the light a small amount
        light.intensity = 0.7;

        this.load_all_in_view(0,0,scene);

        scene.onPointerObservable.add((pointerInfo) => {
            switch (pointerInfo.type) {
                case BABYLON.PointerEventTypes.POINTERUP:
                    console.log("POINTER UP");
                    console.log(camera.position);
                    this.load_all_in_view(camera.position.x, camera.position.y, scene);
                    break;
                case BABYLON.PointerEventTypes.POINTERPICK:
                    console.log("POINTER PICK");
                    var pickResult = scene.pick(pointerInfo.event.clientX, pointerInfo.event.clientY);
                    //var pickResult = scene.pick(scene.pointerX, scene.pointerY);
                    //BABYLON.STLExport.CreateSTL([pickResult.pickedMesh as BABYLON.Mesh])
                    break;
            }
        });


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
