import os
from unemploymentstudios.crews.asset_generation_crew.asset_generation_crew import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
import freesound 

# Create output directories
os.makedirs("./Game/assets/images", exist_ok=True)
os.makedirs("./Game/assets/audio", exist_ok=True)

# Test image generation
def test_image_generation():
    image_tool = GenerateAndDownloadImageTool()
    result = image_tool._run(
        prompt="A hero character with a sword",
        file_name="./Game/assets/images/hero.png"
    )
    print(f"Image tool result: {result}")

# Test audio generation
def test_audio_generation():
    audio_tool = SearchAndSaveSoundTool()
    result = audio_tool._run(
        query="game background music",
        output_path="./Game/assets/audio/background.mp3"
    )
    print(f"Audio tool result: {result}")

if __name__ == "__main__":
    # test_image_generation()
    test_audio_generation()

