from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import Pydantic Types
from unemploymentstudios.types import FileStructureSpec

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FileStructurePlanningCrew:
    """File Structure Planning Crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Basic configuration
    llm = LLM(model="gpt-4o")

    # Advanced configuration with detailed parameters
    '''
    llm = LLM(
        model="gpt-4o-mini",
        temperature=0.7,        # Higher for more creative outputs
        timeout=120,           # Seconds to wait for response
        max_tokens=4000,       # Maximum length of response
        top_p=0.9,            # Nucleus sampling parameter
        frequency_penalty=0.1, # Reduce repetition
        presence_penalty=0.1,  # Encourage topic diversity
        response_format={"type": "json"},  # For structured outputs
        seed=42               # For reproducible results
    )

    Parameter explanations:
        temperature: Controls randomness (0.0-1.0)
        timeout: Maximum wait time for response
        max_tokens: Limits response length
        top_p: Alternative to temperature for sampling
        frequency_penalty: Reduces word repetition
        presence_penalty: Encourages new topics
        response_format: Specifies output structure
        seed: Ensures consistent outputs

    Models
        Model	     Context Window	    Best For
        GPT-4	     8,192 tokens	    High-accuracy tasks, complex reasoning
        GPT-4 Turbo	 128,000 tokens	    Long-form content, document analysis
        GPT-4o	     128,000 tokens	    Cost-effective large context processing
        GPT-4o-mini  128,000 tokens     Cost-effective large context processing
        o3-mini	     200,000 tokens	    Fast reasoning, complex reasoning
        o1-mini	     128,000 tokens	    Fast reasoning, complex reasoning
        o1-preview	 128,000 tokens	    Fast reasoning, complex reasoning
        o1	         200,000 tokens	    Fast reasoning, complex reasoning
    '''

    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------

    @agent
    def lead_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_developer"],
            llm = self.llm
        )

    @agent
    def system_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["system_architect"],
            llm=self.llm
        )

    @agent
    def technical_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_writer"],
            llm=self.llm
        )

    @agent
    def project_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["project_manager"],
            llm=self.llm
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------

    @task
    def analyze_game_concept(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_game_concept"]
            # llm = self.llm
        )
    @task
    def identify_required_files(self) -> Task:
        return Task(
            config=self.tasks_config["identify_required_files"],
            context=[self.analyze_game_concept()]
            # llm = self.llm
        )
    @task
    def clarify_file_purposes(self) -> Task:
        return Task(
            config=self.tasks_config["clarify_file_purposes"],
            context=[self.analyze_game_concept(),self.identify_required_files()]
            # llm = self.llm
        )
    @task
    def define_content_guidelines(self) -> Task:
        return Task(
            config=self.tasks_config["define_content_guidelines"],
            context=[self.analyze_game_concept(),self.identify_required_files(),self.clarify_file_purposes()]
            # llm = self.llm
        )
    @task
    def map_file_dependencies(self) -> Task:
        return Task(
            config=self.tasks_config["map_file_dependencies"],
            context=[self.analyze_game_concept(),self.identify_required_files(),self.clarify_file_purposes(),self.define_content_guidelines()]
            # llm = self.llm
        )
    @task
    def compile_final_file_structure_spec(self) -> Task:
        return Task(
            config=self.tasks_config["compile_final_file_structure_spec"],
            context=[
                self.analyze_game_concept(),
                self.identify_required_files(),
                self.clarify_file_purposes(),self.define_content_guidelines(),self.map_file_dependencies()],
            output_pydantic=FileStructureSpec
            # llm = self.llm
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    @crew
    def crew(self) -> Crew:
        """Create the crew"""
        return Crew(
            agents=self.agents,
            # agents=[agent for agent in self.agents if agent != self.project_manager()],
            tasks=self.tasks,
            process=Process.sequential,
            # process=Process.hierarchical,
            # manager_agent = self.project_manager(),
            # manager_llm = self.llm,
            # function_calling_llm=self.llm,
            # planning=True,
            # planning_llm=self.llm,
            # cache=True,
            # memory=True,
            # embedder={
            #     "provider": "ollama",
            #     "config": {
            #         "model": "mxbai-embed-large"
            #     }
            # },
            verbose=True
        )
        