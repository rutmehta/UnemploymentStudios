```javascript
import { initializeGame } from './main.js';
import { startGame } from './game.js';

const assets = [
    'image1.png',
    'image2.png',
    'sound1.mp3',
    'sound2.mp3',
    'data1.json'
];

function preloadAssets() {
    let loadedAssets = 0;

    const loadAsset = (asset) => {
        return new Promise((resolve, reject) => {
            const assetType = asset.split('.').pop();

            let element;
            switch (assetType) {
                case 'png':
                    element = new Image();
                    element.src = asset;
                    break;

                case 'mp3':
                    element = new Audio();
                    element.src = asset;
                    break;

                case 'json':
                    fetch(asset)
                        .then(response => response.json())
                        .then(data => resolve(data))
                        .catch(error => reject(error));
                    break;
                default:
                    reject(`Unsupported asset type: ${assetType}`);
                    return;
            }

            if (element) {
                element.onload = () => resolve(element);
                element.onerror = () => reject(`Failed to load asset: ${asset}`);
            }
        });
    };

    const assetPromises = assets.map(asset => 
        loadAsset(asset).then(() => {
            loadedAssets++;
            console.log(`Loaded ${loadedAssets}/${assets.length} assets`);
        })
    );

    Promise.all(assetPromises)
        .then(() => {
            console.log('All assets loaded');
            initializeGame();
            startGame();
        })
        .catch(error => {
            handleLoadingError(error);
        });
}

function handleLoadingError(error) {
    console.error("Asset load error: ", error);
}

export { preloadAssets };
```