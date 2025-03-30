from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import Pydantic Types
from unemploymentstudios.types import GameFile

@CrewBase
class AssetGenerationCrew:
    """Asset Generation Crew for game development"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Basic configuration
    llm = LLM(model="gpt-4o")

    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    @agent
    def graphic_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["graphic_designer"],
            llm=self.llm
        )

    @agent
    def sound_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["sound_designer"],
            llm=self.llm
        )

    @agent
    def ui_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_designer"],
            llm=self.llm
        )

    @agent
    def asset_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["asset_manager"],
            llm=self.llm
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    @task
    def analyze_asset_requirements(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_asset_requirements"]
        )

    @task
    def design_character_assets(self) -> Task:
        return Task(
            config=self.tasks_config["design_character_assets"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def design_environment_assets(self) -> Task:
        return Task(
            config=self.tasks_config["design_environment_assets"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def design_ui_elements(self) -> Task:
        return Task(
            config=self.tasks_config["design_ui_elements"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def create_sound_effects(self) -> Task:
        return Task(
            config=self.tasks_config["create_sound_effects"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def create_background_music(self) -> Task:
        return Task(
            config=self.tasks_config["create_background_music"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def finalize_assets(self) -> Task:
        return Task(
            config=self.tasks_config["finalize_assets"],
            context=[
                self.analyze_asset_requirements(),
                self.design_character_assets(),
                self.design_environment_assets(),
                self.design_ui_elements(),
                self.create_sound_effects(),
                self.create_background_music()
            ]
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    @crew
    def crew(self) -> Crew:
        """Create the crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
