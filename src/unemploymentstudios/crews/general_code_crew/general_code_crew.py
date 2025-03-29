from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import Pydantic Types
from unemploymentstudios.types import GameFile

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class GeneralCodeCrew:
    """General Code Crew"""
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
    def full_stack_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["full_stack_developer"],
            llm=self.llm
        )

    @agent
    def javascript_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["javascript_developer"],
            llm=self.llm
        )

    @agent
    def ui_ux_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_ux_designer"],
            llm=self.llm
        )

    @agent
    def code_finalizer(self) -> Agent:
        return Agent(
            config=self.agents_config["code_finalizer"],
            llm=self.llm
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    @task
    def plan(self) -> Task:
        return Task(
            config=self.tasks_config["plan"]
            # llm = self.llm
        )

    @task
    def generate_draft(self) -> Task:
        return Task(
            config=self.tasks_config["generate_draft"],
            context=[self.plan()]
            # llm = self.llm
        )

    @task
    def review_and_refine_full_stack(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_refine_full_stack"],
            context=[
                self.plan(), 
                self.generate_draft()
            ]
            # llm = self.llm
        )

    @task
    def review_and_refine_javascript(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_refine_javascript"],
            context=[
                self.plan(), 
                self.generate_draft(), 
                self.review_and_refine_full_stack()
            ]
            # llm = self.llm
        )

    @task
    def review_and_refine_ui_ux(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_refine_ui_ux"],
            context=[
                self.plan(),
                self.generate_draft(),
                self.review_and_refine_full_stack(),
                self.review_and_refine_javascript()
            ]
            # llm = self.llm
        )

    @task
    def finalize_output(self) -> Task:
        return Task(
            config=self.tasks_config["finalize_output"],
            context=[
                self.plan(),
                self.generate_draft(),
                self.review_and_refine_full_stack(),
                self.review_and_refine_javascript(),
                self.review_and_refine_ui_ux()
            ],
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
            tasks=self.tasks,
            process=Process.sequential,
            # process=Process.hierarchical,
            # manager_agent = self.manager_agent(),
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
        