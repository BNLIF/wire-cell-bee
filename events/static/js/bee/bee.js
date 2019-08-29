// import * as util from './util.js'
import { store } from './store.js'
import { Scene3D } from './scene.js'
import { Canvas } from './canvas.js'
import { Helper } from './helper.js'
import { Gui } from './gui.js'


// console.log(new ProtoDUNE());
// console.log(new ICARUS());
// console.log(new DUNE10ktWorkspace());
// console.log(new DUNE35t());
// console.log(exp.toLocalXYZ([0, 0, 0]));


class Bee {
    constructor() {
        this.scene3d = new Scene3D();
        this.canvas = new Canvas();
        store.xhr.scene3d.then(() => {
            let scene = this.scene3d.scene.main;
            this.helper = new Helper(scene, store);
            this.gui = new Gui(store, this);
        })
    }
}

let bee = new Bee();
console.log('store: ', store);
console.log('bee:', bee);

