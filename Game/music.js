```javascript
const audioFilePath = ['assets/sound/', 'sound/dynamic/'];
let audioContext;
const audioFiles = {
    ambient: 'ambient.mp3',
    exploration: 'exploration.mp3',
    bossBattle: 'boss_battle.mp3'
};
let currentTrack = null;
let gainNode;

const initAudioContext = () => {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    gainNode = audioContext.createGain();
    gainNode.connect(audioContext.destination);
};

const loadAudioFile = async (path) => {
    const response = await fetch(path);
    const arrayBuffer = await response.arrayBuffer();
    return audioContext.decodeAudioData(arrayBuffer);
};

const audioBuffers = {};

const preloadAudio = async () => {
    for (let key in audioFiles) {
        for (let directory of audioFilePath) {
            try {
                audioBuffers[key] = await loadAudioFile(directory + audioFiles[key]);
                break;
            } catch (error) {
                console.error(`Failed to load audio from ${directory}${audioFiles[key]}, trying next directory.`);
            }
        }
    }
};

const identifySegment = (gameState) => {
    switch (gameState) {
        case 'ambient':
            return 'ambient';
        case 'exploration':
            return 'exploration';
        case 'boss_battle':
            return 'bossBattle';
        default:
            return 'ambient';
    }
};

const playAudio = (segment) => {
    if (currentTrack) {
        currentTrack.stop();
    }
    
    const track = audioContext.createBufferSource();
    track.buffer = audioBuffers[segment];
    track.connect(gainNode);
    track.start();
    currentTrack = track;
};

const pauseAudio = () => {
    if (currentTrack) {
        currentTrack.stop();
    }
};

const adjustIntensity = (intensityLevel) => {
    gainNode.gain.setValueAtTime(intensityLevel, audioContext.currentTime);
};

const gameEventHandler = (event) => {
    const segment = identifySegment(event.state);
    playAudio(segment);

    const intensityLevel = event.state === 'boss_battle' ? 1.0 : 0.5;
    adjustIntensity(intensityLevel);
};

const cleanUpAudioResources = () => {
    if (audioContext) {
        audioContext.close();
    }
};

initAudioContext();
preloadAudio().catch(error => console.error("Error preloading audio files: ", error));
```