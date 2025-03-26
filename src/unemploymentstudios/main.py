#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

# Import Crews
from unemploymentstudios.crews.concept_expansion_crew.concept_expansion_crew import ConceptExpansionCrew

# Additional Imports
import os
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
    
    outputGameConcept: str = ""

class GameFlow(Flow[GameState]):
    @start()
    def start_game(self):

        # Load JSON
        f = open("/home/admiralx/Desktop/unemploymentstudios/src/unemploymentstudios/knowledge/concept.json")
        concept = json.load(f)
        f.close()

    @listen(start_game)
    def concept_expansion(self):
        
        output = (
            ConceptExpansionCrew()
            .crew()
            .kickoff(inputs={"Storyline": self.state.Storyline, "Game_Mechanics":self.state.Game_Mechanics, "Entities":self.state.Entities, "Levels":self.state.Levels, "visualAudioStyle":self.state.visualAudioStyle})
        )

        self.state.outputGameConcept = output.raw

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
            f.write(self.state.outputGameConcept)

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

