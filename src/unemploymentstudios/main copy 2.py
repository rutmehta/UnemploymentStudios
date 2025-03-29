#!/usr/bin/env python
from typing import Dict
from random import randint
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start

# Import Crews
from unemploymentstudios.crews.concept_expansion_crew.concept_expansion_crew import ConceptExpansionCrew
from unemploymentstudios.crews.file_structure_planning_crew.file_structure_planning_crew import FileStructurePlanningCrew
from unemploymentstudios.crews.general_code_crew.general_code_crew import GeneralCodeCrew

# Import Pydantic Types
from unemploymentstudios.types import GameConcept

# Additional Imports
import os
import asyncio
import time
import json

# Load concept BEFORE GameState class definition
with open("/home/admiralx/Desktop/unemploymentstudios/src/unemploymentstudios/knowledge/concept.json") as f:
    concept = json.load(f)

class GameState(BaseModel):
    Storyline: str = concept["Storyline"]
    Game_Mechanics: str = concept["Game mechanics"]
    Entities: str = concept["Characters and Interactive entities"]
    Levels: str = concept["Levels and difficulty"]
    visualAudioStyle: str =concept["Visual and audio style"]
    
    conceptExpansionOutput: str = ""
    fileStructurePlanningOutput: str = ""

    # Add this line so we have a place to store generated code
    generatedCodeFiles: Dict[str, str] = Field(default_factory=dict)

class GameFlow(Flow[GameState]):
    @start()
    def start_game(self):
        print("")

    @listen(start_game)
    def concept_expansion(self):
        
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

    @listen(concept_expansion)
    def save_concept(self):
        
        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "game_concept.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        # os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/game_concept.txt", "w") as f:
            f.write(self.state.conceptExpansionOutput)

    @listen(save_concept)
    def file_structure_planning(self):
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

        '''
        # 1. Parse the JSON string from conceptExpansionOutput into a dict
        expanded_concept_data = json.loads(self.state.conceptExpansionOutput)

        # 2. Pass the individual fields to the FileStructurePlanningCrew
        file_structure_planning_raw = (
            FileStructurePlanningCrew()
            .crew()
            .kickoff(inputs={
                "title": expanded_concept_data["title"],
                "tagline": expanded_concept_data["tagline"],
                "overview": expanded_concept_data["overview"],
                "main_character": expanded_concept_data["main_character"],
                "supporting_characters": expanded_concept_data["supporting_characters"],
                "world_building": expanded_concept_data["world_building"],
                "levels": expanded_concept_data["levels"],
                "gameplay_mechanics": expanded_concept_data["gameplay_mechanics"],
                "visual_style": expanded_concept_data["visual_style"],
                "audio_style": expanded_concept_data["audio_style"],
                "emotional_arc": expanded_concept_data["emotional_arc"],
                "conclusion": expanded_concept_data["conclusion"],
            })
        )
        '''

        self.state.fileStructurePlanningOutput = file_structure_planning_raw.raw

    @listen(file_structure_planning)
    def save_file_structure(self):

        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "file_structure.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        # os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/file_structure.txt", "w") as f:
            f.write(self.state.fileStructurePlanningOutput)

    @listen(save_file_structure)
    async def write_code_files(self):
        """
        Parse the file structure planning output,
        spawn ONE code-writing crew just for the first file,
        and save the result to disk.
        """
        print("=== Generating code for the first file only ===")

        # Parse the file structure planning output into a Python list or dict
        # Adjust the parsing to match whatever data shape you get back

        # --- Option A: Use raw JSON to grab the array of files ---
        file_structure = json.loads(self.state.fileStructurePlanningOutput)
        files = file_structure["files"]  # This is the array of file specs

        # If no files, exit early
        if not files:
            print("No files found in file structure, skipping code generation.")
            return

        # We'll only generate code for the FIRST file
        first_file_info = files[0]

        def guess_filetype(filename: str) -> str:
            filename_lower = filename.lower()
            if filename_lower.endswith(".html"):
                return "html"
            elif filename_lower.endswith(".css"):
                return "css"
            elif filename_lower.endswith(".js"):
                return "js"
            elif filename_lower.endswith(".json"):
                return "json"
            elif "/assets/audio/" in filename_lower:
                return "audio"
            # If it's clearly a directory or doesn't match known exts, treat as asset
            else:
                return "asset"

        # Simple mapping from filetype to "responsible crew"
        crew_map = {
            "html": "HTML Crew",
            "css": "CSS Crew",
            "js": "Core JavaScript Crew",
            "audio": "Audio Crew",
            "json": "Data/Config Crew",
            "asset": "Asset Crew"
        }

        # Inner async function to write a single file
        async def write_single_file(file_info):
            # Kick off the dedicated code-writing crew for this single file
            result = (
                GeneralCodeCrew()
                .crew()
                .kickoff(
                    inputs={
                        "filename": file_info["filename"],
                        "purpose": file_info["purpose"],
                        "content_guidelines": file_info["content_guidelines"],
                        "dependencies": file_info.get("dependencies", []),
                    }
                )
            )

            # Build a response that follows the GameFile model shape
            filetype = guess_filetype(file_info["filename"])
            responsible_crew = crew_map.get(filetype, "General Code Crew")

            # Return a dict that matches the GameFile schema
            # IMPORTANT: Use the key "code" so it matches how we access it later
            return {
                "filename": file_info["filename"],
                "filetype": filetype,                       # Literal["html", "css", "js", "audio", "json", "asset"]
                "code": result.raw,                      # The actual file content from the crew
                "status": "draft",                          # "draft" by default
                "responsible_crew": responsible_crew        # e.g. "Core JavaScript Crew"
            }

        # Actually generate the code for just this one file
        gf = await write_single_file(first_file_info)

        # Save the code in the state
        self.state.generatedCodeFiles[gf["filename"]] = gf["code"]

        # Write the generated file to disk
        output_dir = "./Game"
        os.makedirs(output_dir, exist_ok=True)

        path = os.path.join(output_dir, gf["filename"])
        print(f"Saving generated code to {path}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(gf["code"])

        print("=== Single code file generated and saved ===")


'''
class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


class PoemFlow(Flow[PoemState]):

    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = (
            PoemCrew()
            .crew()
            .kickoff(inputs={"sentence_count": self.state.sentence_count})
        )

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)
'''

def kickoff():
    game_flow = GameFlow()
    game_flow.kickoff()

def plot():
    game_flow = GameFlow()
    game_flow.plot()

if __name__ == "__main__":

    start_time = time.perf_counter()

    kickoff()

    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.4f} seconds")

