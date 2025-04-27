#!/usr/bin/env python
import os
import dotenv
dotenv.load_dotenv(override=True)
from typing import Dict
from random import randint
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start

# Import Crews
from unemploymentstudios.crews.concept_expansion_crew.concept_expansion_crew import ConceptExpansionCrew
from unemploymentstudios.crews.file_structure_planning_crew.file_structure_planning_crew import FileStructurePlanningCrew
from unemploymentstudios.crews.general_code_crew.general_code_crew import GeneralCodeCrew
from unemploymentstudios.crews.asset_generation_crew.asset_generation_crew import AssetGenerationCrew
from unemploymentstudios.crews.testing_qa_crew.testing_qa_crew import TestingQACrew

# Import Pydantic Types
from unemploymentstudios.types import GameConcept

# Additional Imports
import asyncio
import time
import json
import shutil
import pathlib
from pathlib import Path

# Load concept from file or create default if it doesn't exist
concept_path = os.path.join(os.path.dirname(__file__), "knowledge", "concept.json")
try:
    with open(concept_path) as f:
        concept = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Create a default concept if file doesn't exist or is invalid
    concept = {
        "Storyline": "A heroic adventure through a magical world",
        "Game mechanics": "Platformer with puzzle-solving elements",
        "Characters and Interactive entities": "A brave hero with magical abilities, various enemies and allies",
        "Levels and difficulty": "Multiple levels with increasing difficulty",
        "Visual and audio style": "Vibrant fantasy world with orchestral music"
    }
    # Ensure the directory exists
    os.makedirs(os.path.dirname(concept_path), exist_ok=True)
    with open(concept_path, "w") as f:
        json.dump(concept, f, indent=2)

def is_directory(path: str) -> bool:
    # For example, treat anything that ends in a slash as a directory
    return path.endswith("/")

class GameState(BaseModel):
    # Concept fields ---------------------------------------------------------
    Storyline: str = concept["Storyline"]
    Game_Mechanics: str = concept["Game mechanics"]
    Entities: str = concept["Characters and Interactive entities"]
    Levels: str = concept["Levels and difficulty"]
    visualAudioStyle: str = concept["Visual and audio style"]

    # Phase outputs ----------------------------------------------------------
    conceptExpansionOutput: str = ""
    fileStructurePlanningOutput: str = ""
    assetGenerationOutput: str = ""
    testingQAOutput: str = ""

    # Generated artefacts ----------------------------------------------------
    generatedCodeFiles: Dict[str, str] = Field(default_factory=dict)
    generatedAssetSpecs: Dict[str, str] = Field(default_factory=dict)
    generatedImages: Dict[str, str] = Field(default_factory=dict)
    generatedSounds: Dict[str, str] = Field(default_factory=dict)
    qaReports: Dict[str, str] = Field(default_factory=dict)

class GameFlow(Flow[GameState]):
    @start()
    def start_game(self):
        print("")
        print("=== Starting Game Generation Process ===")
        print("This process will use multiple AI agents working in crews to generate a complete game")
        print("1. Concept Expansion - Develop detailed game concept")
        print("2. File Structure Planning - Design the codebase architecture")
        print("3. Code Generation - Create the actual game code files")
        print("4. Asset Generation - Create specifications for graphics and audio")
        print("5. Testing & QA - Ensure all components work together")
        print("")

    @listen(start_game)
    def concept_expansion(self):
        print("=== Starting Concept Expansion Phase ===")
        
        concept_expansion_raw = (
            ConceptExpansionCrew()
            .crew()
            .kickoff(inputs={
                "Storyline": self.state.Storyline, 
                "Game_Mechanics":self.state.Game_Mechanics, 
                "Entities":self.state.Entities, 
                "Levels":self.state.Levels, 
                "visualAudioStyle":self.state.visualAudioStyle
            })
        )

        self.state.conceptExpansionOutput = concept_expansion_raw.raw
        print("=== Concept Expansion Phase Complete ===")

    @listen(concept_expansion)
    def save_concept(self):
        print("=== Saving Expanded Game Concept ===")
        
        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "game_concept.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/game_concept.txt", "w") as f:
            f.write(self.state.conceptExpansionOutput)
            
        print(f"Saved expanded game concept to {file_path}")

    @listen(save_concept)
    def file_structure_planning(self):
        print("=== Starting File Structure Planning Phase ===")
        
        # 1. Parse JSON string into a Pydantic model.
        expanded_concept = GameConcept(**json.loads(self.state.conceptExpansionOutput))

        # For supporting_characters, turn each Character object into a dict
        supporting_characters_as_dicts = [char.dict() for char in expanded_concept.supporting_characters]
        # Same for levels (turn each Level object into a dict)
        levels_as_dicts = [lvl.dict() for lvl in expanded_concept.levels]

        # Build a dictionary for the base fields (non-list)
        inputs_dict = {
            "title": expanded_concept.title,
            "tagline": expanded_concept.tagline,
            "overview": expanded_concept.overview,
            "main_character": expanded_concept.main_character.name,
            "main_character_name": expanded_concept.main_character.name,
            "main_character_role": expanded_concept.main_character.role,
            "main_character_abilities": expanded_concept.main_character.abilities,
            "main_character_description": expanded_concept.main_character.description,
            "main_character_emotional_arc": expanded_concept.main_character.emotional_arc,
            "supporting_characters": supporting_characters_as_dicts,
            "supporting_characters|length": len(expanded_concept.supporting_characters),
            "world_building": expanded_concept.world_building,
            "levels": levels_as_dicts,
            "levels|length": len(expanded_concept.levels),
            "gameplay_mechanics": expanded_concept.gameplay_mechanics,
            "visual_style": expanded_concept.visual_style,
            "audio_style": expanded_concept.audio_style,
            "emotional_arc": expanded_concept.emotional_arc,
            "conclusion": expanded_concept.conclusion,
        }

        #
        # 2. Precompute placeholders for each supporting character
        #
        character_inputs = {}
        for idx, char in enumerate(expanded_concept.supporting_characters):
            prefix = f"supporting_characters_{idx}_"
            character_inputs[f"{prefix}name"] = char.name
            character_inputs[f"{prefix}role"] = char.role
            character_inputs[f"{prefix}description"] = char.description
            character_inputs[f"{prefix}abilities"] = char.abilities
            character_inputs[f"{prefix}emotional_arc"] = char.emotional_arc

        #
        # 3. Precompute placeholders for each level
        #
        level_inputs = {}
        for idx, lvl in enumerate(expanded_concept.levels):
            prefix = f"levels_{idx}_"
            level_inputs[f"{prefix}name"] = lvl.name
            level_inputs[f"{prefix}description"] = lvl.description
            level_inputs[f"{prefix}difficulty"] = lvl.difficulty
            level_inputs[f"{prefix}key_objectives"] = lvl.key_objectives
            level_inputs[f"{prefix}enemies_obstacles"] = lvl.enemies_obstacles
            level_inputs[f"{prefix}boss_battle"] = lvl.boss_battle

        #
        # 3a. Also define the first/last-level placeholders that match tasks.yaml
        #
        # Only do this if at least one level exists.
        if expanded_concept.levels:
            first_level = expanded_concept.levels[0]
            inputs_dict["first_level_name"] = first_level.name
            inputs_dict["first_level_difficulty"] = first_level.difficulty
            inputs_dict["first_level_enemies_obstacles"] = first_level.enemies_obstacles

            # If there's a "last" level distinct from the first, define placeholders from that too:
            last_level = expanded_concept.levels[-1]
            inputs_dict["last_level_name"] = last_level.name
            inputs_dict["last_level_difficulty"] = last_level.difficulty
            inputs_dict["last_level_boss_battle"] = last_level.boss_battle

            # For tasks referencing all level names in a single string (e.g., {levels_names}):
            level_names = [lvl.name for lvl in expanded_concept.levels]
            inputs_dict["levels_names"] = ", ".join(level_names)

        # Merge our custom loops into the main inputs_dict
        inputs_dict.update(character_inputs)
        inputs_dict.update(level_inputs)

        # 4. Kick off your crew with the full dictionary of placeholders
        file_structure_planning_raw = (
            FileStructurePlanningCrew()
            .crew()
            .kickoff(inputs=inputs_dict)
        )

        self.state.fileStructurePlanningOutput = file_structure_planning_raw.raw
        print("=== File Structure Planning Phase Complete ===")

    @listen(file_structure_planning)
    def save_file_structure(self):
        print("=== Saving File Structure Plan ===")

        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "file_structure.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/file_structure.txt", "w") as f:
            f.write(self.state.fileStructurePlanningOutput)
            
        print(f"Saved file structure plan to {file_path}")

    @listen(save_file_structure)
    async def write_code_files(self):
        """
        Parse the file structure planning output, 
        spawn an async writing job for each file, and await them concurrently.
        """
        print("=== Starting Code Generation Phase ===")
        print("Generating code files concurrently...")

        # Parse the file structure planning output into a Python list or dict
        # Adjust the parsing to match whatever data shape you get back

        # --- Option A: Use raw JSON to grab the array of files ---
        file_structure = json.loads(self.state.fileStructurePlanningOutput)
        files = file_structure["files"]  # This is the array of file specs

        # If no files, exit early
        if not files:
            print("No files to generate. Check file structure output.")
            return

        # Create a list to store all tasks that we'll await concurrently
        tasks = []
        
        # For each file specification, create and launch an async task
        for file_spec in files:
            task = asyncio.create_task(
                self._generate_file_code(file_spec)
            )
            tasks.append(task)
        
        # Wait for all file generation tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Process results (store in state, etc.)
        for result in results:
            if result:  # Skip any None results
                filename, content = result
                # Store in state dictionary
                self.state.generatedCodeFiles[filename] = content
                
                # Write the file to disk
                self._write_file_to_disk(filename, content)
        
        print(f"=== Generated {len(self.state.generatedCodeFiles)} code files ===")

    async def _generate_file_code(self, file_spec):
        """
        Generate code for a single file using the GeneralCodeCrew
        """
        filename = file_spec["filename"]
        purpose = file_spec["purpose"]
        content_guidelines = file_spec["content_guidelines"]
        dependencies = file_spec.get("dependencies", [])
        
        print(f"Generating code for: {filename}")
        
        try:
            # Use GeneralCodeCrew to generate the file content
            file_result = (
                GeneralCodeCrew()
                .crew()
                .kickoff(inputs={
                    "filename": filename,
                    "purpose": purpose,
                    "content_guidelines": content_guidelines,
                    "dependencies": dependencies
                })
            )
            
            # Return the filename and content
            return filename, file_result.raw
        except Exception as e:
            print(f"Error generating code for {filename}: {str(e)}")
            return None
        
    def _write_file_to_disk(self, filename: str, content: str):
        """
        Write a generated file to disk, skipping folder‑only entries.
        """
        output_dir = "./Game"

        # Skip any paths that try to write outside the Game directory
        if filename.startswith('/'):
            print(f"Warning: Skipping file with absolute path: {filename}")
            # Store a sanitized version in the state
            safe_filename = filename.lstrip('/')
            self.state.generatedCodeFiles[safe_filename] = content
            return

        # ── 1️⃣ Ignore or create directory‑only specs ───────────────────────────────
        if filename.endswith("/") or os.path.basename(filename) == "":
            try:
                dir_path = os.path.join(output_dir, filename)
                os.makedirs(dir_path, exist_ok=True)
                print(f"Created directory (no file to write): {dir_path}")
            except OSError as e:
                print(f"Warning: Could not create directory {dir_path}: {e}")
            return

        # ── 2️⃣ Ensure parent folders exist (unchanged) ────────────────────────────
        if "/" in filename:
            sub_path = os.path.dirname(filename)
            full_dir_path = os.path.join(output_dir, sub_path)
            try:
                os.makedirs(full_dir_path, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory {full_dir_path}: {e}")
                # Skip file creation if we can't create the directory
                return

        # ── 3️⃣ Write the file (unchanged) ─────────────────────────────────────────
        file_path = os.path.join(output_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Wrote file: {file_path}")
        except OSError as e:
            print(f"Warning: Could not write file {file_path}: {e}")
            # Store the content in state even if we couldn't write to disk
            self.state.generatedCodeFiles[filename] = content

    @listen(save_file_structure)
    async def write_code_files(self):
        """
        Parse the file structure planning output, 
        spawn an async writing job for each file, and await them concurrently.
        """
        print("=== Starting Code Generation Phase ===")
        print("Generating code files concurrently...")

        # Parse the file structure planning output into a Python list or dict
        # Adjust the parsing to match whatever data shape you get back

        # --- Option A: Use raw JSON to grab the array of files ---
        file_structure = json.loads(self.state.fileStructurePlanningOutput)
        files = file_structure["files"]  # This is the array of file specs

        # If no files, exit early
        if not files:
            print("No files to generate. Check file structure output.")
            return

        # Create a list to store all tasks that we'll await concurrently
        tasks = []
        
        # For each file specification, create and launch an async task
        for file_spec in files:
            task = asyncio.create_task(
                self._generate_file_code(file_spec)
            )
            tasks.append(task)
        
        # Wait for all file generation tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Process results (store in state, etc.)
        for result in results:
            if result:  # Skip any None results
                filename, content = result
                # Store in state dictionary
                self.state.generatedCodeFiles[filename] = content
                
                # Write the file to disk
                self._write_file_to_disk(filename, content)
        
        print(f"=== Generated {len(self.state.generatedCodeFiles)} code files ===")

    @listen(write_code_files)
    def generate_assets(self):
        """
        Generate game assets *and* store the actual image / sound files
        in a sane directory structure inside ./Game/assets/.
        """
        print("=== Starting Asset Generation Phase ===")

        # Create asset directories
        try:
            os.makedirs("./Game/assets/images", exist_ok=True)
            os.makedirs("./Game/assets/audio", exist_ok=True)
            os.makedirs("./assets/images", exist_ok=True)
            os.makedirs("./assets/audio", exist_ok=True)
            os.makedirs("./public/assets/images", exist_ok=True)
            os.makedirs("./public/assets/audio", exist_ok=True)
            print("Created asset directories")
        except OSError as e:
            print(f"Warning: Could not create asset directories: {e}")

        # Direct testing of tools before running crew
        try:
            print("Testing image generation tool directly...")
            from unemploymentstudios.crews.asset_generation_crew.asset_generation_crew import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
            
            # Test if API keys are available
            print(f"OPENAI_API_KEY available: {bool(os.getenv('OPENAI_API_KEY'))}")
            print(f"FREESOUND_API_KEY available: {bool(os.getenv('FREESOUND_API_KEY'))}")
            
            # Test image generation directly
            test_image = GenerateAndDownloadImageTool()
            image_result = test_image._run(
                prompt="Test image for game - a simple game logo",
                file_name="./assets/images/test_direct.png"
            )
            print(f"Direct image tool test result: {image_result}")
            
            # Test audio generation directly
            test_audio = SearchAndSaveSoundTool()
            audio_result = test_audio._run(
                query="game background music",
                output_path="./assets/audio/test_direct.mp3"
            )
            print(f"Direct audio tool test result: {audio_result}")
        except Exception as e:
            print(f"Direct tool testing error: {e}")

        # 1. Prepare crew inputs exactly as before
        try:
            expanded_concept = GameConcept(**json.loads(self.state.conceptExpansionOutput))
            asset_inputs = {
                "main_character": expanded_concept.main_character.dict(),
                "supporting_characters": [c.dict() for c in expanded_concept.supporting_characters],
                "world_building": expanded_concept.world_building,
                "levels": [l.dict() for l in expanded_concept.levels],
                "visual_style": expanded_concept.visual_style,
                "audio_style": expanded_concept.audio_style,
                "title": expanded_concept.title,
                # Add explicit instructions to ensure tool usage
                "force_tool_usage": True,
                "required_image_count": 5,  # Minimum number of images to generate
                "required_audio_count": 3,  # Minimum number of audio files to generate
                "image_generation_instruction": "You MUST call the generate_and_download_image tool for every asset",
                "audio_generation_instruction": "You MUST call the search_and_save_sound tool for every sound",
            }

            print(f"Prepared asset inputs: {asset_inputs.keys()}")

            # 2. Kick off the AssetGenerationCrew
            print("Starting AssetGenerationCrew...")
            asset_result = (
                AssetGenerationCrew()
                .crew()
                .kickoff(inputs=asset_inputs)
            )
            print(f"Asset crew result type: {type(asset_result)}")
            print(f"Asset crew result has raw: {'raw' in dir(asset_result)}")
            
            self.state.assetGenerationOutput = asset_result.raw
            print(f"Asset generation output length: {len(self.state.assetGenerationOutput)}")

            # Output a snippet to help debug
            output_preview = self.state.assetGenerationOutput[:500] + "..." if len(self.state.assetGenerationOutput) > 500 else self.state.assetGenerationOutput
            print(f"Asset generation output preview: {output_preview}")

            # 3. Copy everything into ./Game/assets/
            print("Running _organise_generated_assets...")
            self._organise_generated_assets()

            # 4. Save raw log for transparency
            with open("./Game/asset_generation_log.txt", "w") as f:
                f.write(self.state.assetGenerationOutput)

            print("Asset generation & copying complete.")

        except Exception as e:
            print(f"[Asset Generation] Error: {e}")
        print("=== Asset Generation Phase Complete ===")

    # -----------------------------------------------------------------------
    #                          NEW helper methods
    # -----------------------------------------------------------------------
    def _organise_generated_assets(self):
        """
        Copy manifests + actual files produced by AssetGenerationCrew into
        the canonical ./Game/assets folder.
        """
        game_assets_root = pathlib.Path("./Game/assets")
        images_dir = game_assets_root / "images"
        audio_dir = game_assets_root / "audio"
        game_assets_root.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        audio_dir.mkdir(exist_ok=True)

        # default locations produced by our crew
        crew_assets_root = pathlib.Path("./assets")
        public_root = pathlib.Path("./public/assets")  # in case Integrator used this

        # 1️⃣ Copy manifest files if they exist
        for src in [
            crew_assets_root / "manifest_images.json",
            crew_assets_root / "manifest_audio.json",
            public_root / "manifest_images.json",
            public_root / "manifest_audio.json",
        ]:
            if src.exists():
                shutil.copy2(src, game_assets_root / src.name)

        # 2️⃣ Walk through likely asset locations and copy files
        for candidate_root in [crew_assets_root, public_root]:
            if not candidate_root.exists():
                continue
            for path in candidate_root.rglob("*"):
                if path.is_file():
                    # Decide destination sub‑dir (images vs audio vs other)
                    lower = path.suffix.lower()
                    if lower in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                        dest = images_dir / path.name
                        shutil.copy2(path, dest)
                        self.state.generatedImages[path.name] = str(dest)
                    elif lower in {".wav", ".mp3", ".ogg"}:
                        dest = audio_dir / path.name
                        shutil.copy2(path, dest)
                        self.state.generatedSounds[path.name] = str(dest)
                    # else: ignore (could add fonts or fx later)

        # 3️⃣ Simple console summary
        print(f"  Copied {len(self.state.generatedImages)} images "
              f"and {len(self.state.generatedSounds)} audio files into Game/assets.")
    @listen(generate_assets)
    def test_game(self):
        """
        Run tests on the generated game code.
        """
        print("=== Starting Testing & QA Phase ===")
        
        try:
            # Create inputs for the testing and QA crew
            code_files = {filename: content for filename, content in self.state.generatedCodeFiles.items()}
            
            # Only include key files to avoid overwhelming the crew
            key_files = {
                k: v for k, v in code_files.items() 
                if k.endswith('.js') or k.endswith('.html') or k.endswith('.css')
            }
            
            # Simplify testing by only including essential files if there are too many
            if len(key_files) > 5:
                # Prioritize main files
                priority_files = {}
                for name in ['index.html', 'main.js', 'game.js', 'style.css']:
                    if name in key_files:
                        priority_files[name] = key_files[name]
                
                # If we don't have at least 3 files, add more until we do
                if len(priority_files) < 3:
                    for name, content in key_files.items():
                        if name not in priority_files:
                            priority_files[name] = content
                            if len(priority_files) >= 3:
                                break
                
                test_inputs = {"code_files": priority_files}
            else:
                test_inputs = {"code_files": key_files}
            
            # Add concept information
            if self.state.conceptExpansionOutput:
                test_inputs["game_concept"] = self.state.conceptExpansionOutput
            
            # Use TestingQACrew to test the game
            test_result = (
                TestingQACrew()
                .crew()
                .kickoff(inputs=test_inputs)
            )
            
            # Store the testing output
            self.state.testingQAOutput = test_result.raw
            
            # Save testing report to file
            with open("./Game/qa_report.txt", "w") as f:
                f.write(self.state.testingQAOutput)
                
            print("QA testing completed successfully")
            
        except Exception as e:
            print(f"Error in testing phase: {str(e)}")
            
            # Create a minimal test report as fallback
            test_report = """
            # Game Test Report
            
            A comprehensive test of the generated game code would be performed here.
            
            ## Testing Areas
            - Functionality testing
            - Performance testing
            - Usability testing
            - Compatibility testing
            
            ## Results
            Placeholder for test results
            """
            
            # Write test report to file
            with open("./Game/test_report.md", "w") as f:
                f.write(test_report)
                
            print("Created fallback test_report.md")
            
        print("=== Testing & QA Phase Complete ===")

    @listen(test_game)
    def finalize_game(self):
        """
        Final steps to prepare the game for deployment.
        """
        print("=== Game Finalization Phase ===")
        
        # Create a README.md for the game
        readme_content = f"""
        # {self.state.Storyline.split()[0] if self.state.Storyline else "Game"} - Generated by UnemploymentStudios
        
        This game was automatically generated using CrewAI and UnemploymentStudios.
        
        ## How to Run
        
        1. Open the `index.html` file in a modern web browser
        2. Alternatively, use a local server:
           ```
           python -m http.server
           ```
           Then visit http://localhost:8000
        
        ## Game Concept
        
        {self.state.Storyline}
        
        ## Game Mechanics
        
        {self.state.Game_Mechanics}
        
        ## Credits
        
        Generated by UnemploymentStudios using CrewAI
        """
        
        # Write README to file
        with open("./Game/README.md", "w") as f:
            f.write(readme_content)
            
        print("Created README.md for the game")
        
        # Create an index.html launcher if it doesn't exist
        # This ensures we have at least one working file to preview the game
        if not os.path.exists("./Game/index.html"):
            fallback_index = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Game by UnemploymentStudios</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; }
                    .game-container { width: 800px; height: 600px; margin: 20px auto; background-color: #fff; border: 2px solid #333; }
                    header { text-align: center; padding: 20px; }
                    footer { text-align: center; padding: 10px; font-size: 0.8em; color: #666; }
                </style>
            </head>
            <body>
                <header>
                    <h1>Game by UnemploymentStudios</h1>
                </header>
                
                <div class="game-container" id="game-container">
                    <h2 style="text-align: center; padding-top: 250px;">Game Loading...</h2>
                </div>
                
                <footer>
                    <p>Created with CrewAI and UnemploymentStudios</p>
                </footer>
                
                <script>
                    // Check if game.js exists, otherwise display a message
                    document.addEventListener('DOMContentLoaded', function() {
                        const gameScript = document.createElement('script');
                        gameScript.src = 'game.js';
                        gameScript.onerror = function() {
                            document.getElementById('game-container').innerHTML = 
                                '<div style="text-align: center; padding-top: 250px;"><h2>Game files are still being generated</h2>' +
                                '<p>Check the generated files in the Game directory</p></div>';
                        };
                        document.body.appendChild(gameScript);
                    });
                </script>
            </body>
            </html>
            """
            
            with open("./Game/index.html", "w") as f:
                f.write(fallback_index)
                
            print("Created fallback index.html")
        
        print("=== Game Generation Complete ===")
        print("")
        print("Your game has been generated in the ./Game directory!")
        print("Open ./Game/index.html in a web browser to play.")
        print("View ./Game/file_structure.txt for the codebase organization.")
        print("View ./Game/game_concept.txt for the detailed game concept.")
        print("")

def kickoff():
    game_flow = GameFlow()
    flow_result = game_flow.kickoff()

def plot():
    return "UnemploymentStudios Flow Diagram"

if __name__ == "__main__":
    start_time = time.perf_counter()
    
    # Display welcome message
    print("")
    print("=" * 80)
    print("               UnemploymentStudios Game Generator                ")
    print("=" * 80)
    print("This tool will generate a complete web-based game using CrewAI.")
    print("The process takes several minutes as multiple AI agents work together.")
    print("=" * 80)
    print("")
    
    # Start the flow
    kickoff()

    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.4f} seconds")