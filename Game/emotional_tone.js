```javascript
// emotional_tone.js

import { playSoundtrack, stopSoundtrack } from './music.js';

const EMOTIONS = {
  HAPPY: 'happy',
  SAD: 'sad',
  ANGRY: 'angry',
};

const NARRATIVE_ARCS = {
  INTRO: 'intro',
  CLIMAX: 'climax',
  RESOLUTION: 'resolution',
};

const characterEmotionMap = {
  hero: {
    currentEmotion: EMOTIONS.HAPPY,
    dialogueOptions: {
      [EMOTIONS.HAPPY]: "I'm feeling great today!",
      [EMOTIONS.SAD]: "Life is tough sometimes.",
      [EMOTIONS.ANGRY]: "I won't let this stand!",
    },
  },
};

const narrativeEmotionInfluence = {
  [NARRATIVE_ARCS.INTRO]: EMOTIONS.HAPPY,
  [NARRATIVE_ARCS.CLIMAX]: EMOTIONS.ANGRY,
  [NARRATIVE_ARCS.RESOLUTION]: EMOTIONS.SAD,
};

function detectEmotion(character, currentNarrativeArc) {
  const narrativeInfluence = narrativeEmotionInfluence[currentNarrativeArc];
  return characterEmotionMap[character].currentEmotion || narrativeInfluence;
}

function adjustDialogue(character) {
  const currentEmotion = detectEmotion(character, currentNarrativeArc);
  const dialogue = characterEmotionMap[character].dialogueOptions[currentEmotion];
  updateDialogue(character, dialogue);
}

function adjustSoundtrack(currentNarrativeArc) {
  const emotion = narrativeEmotionInfluence[currentNarrativeArc];
  let soundtrackToPlay = '';

  switch (emotion) {
    case EMOTIONS.HAPPY:
      soundtrackToPlay = 'happy_theme.mp3';
      break;
    case EMOTIONS.SAD:
      soundtrackToPlay = 'sad_theme.mp3';
      break;
    case EMOTIONS.ANGRY:
      soundtrackToPlay = 'angry_theme.mp3';
      break;
    default:
      soundtrackToPlay = 'default_theme.mp3';
  }

  stopSoundtrack();
  playSoundtrack(soundtrackToPlay);
}

function onCharacterStateChange(character, newState) {
  characterEmotionMap[character].currentEmotion = newState.emotion;
  adjustDialogue(character);
  adjustSoundtrack(currentNarrativeArc);
}

function updateDialogue(character, dialogue) {
  console.log(`Character: ${character}, Dialogue: ${dialogue}`);
}

let currentNarrativeArc = NARRATIVE_ARCS.INTRO;

function onNarrativeArcChange(newArc) {
  currentNarrativeArc = newArc;
  adjustSoundtrack(currentNarrativeArc);
}

onCharacterStateChange('hero', { emotion: EMOTIONS.HAPPY });
onNarrativeArcChange(NARRATIVE_ARCS.CLIMAX);
```