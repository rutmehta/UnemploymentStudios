#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

# Import Crews
from unemploymentstudios.crews.concept_expansion_crew.concept_expansion_crew import ConceptExpansionCrew
from unemploymentstudios.crews.file_structure_planning_crew.file_structure_planning_crew import FileStructurePlanningCrew
from unemploymentstudios.crews.general_code_crew.general_code_crew import GeneralCodeCrew

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


class GameFlow(Flow[GameState]):
    @start()
    def start_game(self):
        print("")

    @listen(start_game)
    def concept_expansion(self):
        
        concept_expansion_raw = (
            ConceptExpansionCrew()
            .crew()
            .kickoff(inputs={"Storyline": self.state.Storyline, "Game_Mechanics":self.state.Game_Mechanics, "Entities":self.state.Entities, "Levels":self.state.Levels, "visualAudioStyle":self.state.visualAudioStyle})
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

        file_structure_planning_raw = (
            FileStructurePlanningCrew()
            .crew()
            .kickoff()
        )

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
        spawn an async writing job for each file, and await them concurrently.
        """
        print("=== Generating code files concurrently ===")

        # Parse the file structure planning output into a Python list or dict
        # Adjust the parsing to match whatever data shape you get back

        # --- Option A: Use raw JSON to grab the array of files ---
        file_structure = json.loads(self.state.fileStructurePlanningOutput)
        files = file_structure["files"]  # This is the array of file specs
        # --- Option B (commented out): Parse into a Pydantic model ---
        # from your_module import FileStructureSpec
        # file_structure_spec = FileStructureSpec(**json.loads(self.state.fileStructurePlanningOutput))
        # files = file_structure_spec.files

        tasks = []

        # Simple helper to guess filetype from filename or path
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

        # Define an inner async function that spawns a single code-writing crew
        async def write_single_file(file_info):
            # Kick off a dedicated code-writing crew for this file
            result = (
                GeneralCodeCrew()
                .crew()
                .kickoff(
                    inputs={
                        "filename": file_info["filename"],
                        "purpose": file_info["purpose"],
                        "guidelines": file_info["content_guidelines"],
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

        # Schedule each file generation as a separate asyncio task
        # Use `files` (the list) in our loop, not `file_structure` (the dict)
        for file_info in files:
            print(f"Creating code-writing task for file: {file_info['filename']}")
            task = asyncio.create_task(write_single_file(file_info))
            tasks.append(task)

        generated_files = await asyncio.gather(*tasks)

        # Make sure you have a place to store them in state (if desired)
        # If your GameState has generatedCodeFiles = Field(default_factory=dict):
        for gf in generated_files:
            # Save the code in the state
            self.state.generatedCodeFiles[gf["filename"]] = gf["code"]

        # Now write each generated file to disk
        output_dir = "./Game"
        os.makedirs(output_dir, exist_ok=True)

        for gf in generated_files:
            path = os.path.join(output_dir, gf["filename"])
            print(f"Saving generated code to {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(gf["code"])  # Use gf["code"]

        print("=== All code files generated and saved ===")


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

