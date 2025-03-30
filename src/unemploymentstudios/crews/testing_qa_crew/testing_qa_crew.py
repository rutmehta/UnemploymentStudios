from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import Pydantic Types
from unemploymentstudios.types import QAFeedback

@CrewBase
class TestingQACrew:
    """Testing and QA Crew for game development"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Basic configuration
    llm = LLM(model="gpt-4o")

    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    @agent
    def game_tester(self) -> Agent:
        return Agent(
            config=self.agents_config["game_tester"],
            llm=self.llm
        )

    @agent
    def performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["performance_analyst"],
            llm=self.llm
        )

    @agent
    def ux_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config["ux_evaluator"],
            llm=self.llm
        )

    @agent
    def qa_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_lead"],
            llm=self.llm
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    @task
    def analyze_game_code(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_game_code"]
        )

    @task
    def test_gameplay_mechanics(self) -> Task:
        return Task(
            config=self.tasks_config["test_gameplay_mechanics"],
            context=[self.analyze_game_code()]
        )

    @task
    def evaluate_performance(self) -> Task:
        return Task(
            config=self.tasks_config["evaluate_performance"],
            context=[self.analyze_game_code()]
        )

    @task
    def assess_user_experience(self) -> Task:
        return Task(
            config=self.tasks_config["assess_user_experience"],
            context=[self.analyze_game_code(), self.test_gameplay_mechanics()]
        )

    @task
    def identify_bugs(self) -> Task:
        return Task(
            config=self.tasks_config["identify_bugs"],
            context=[self.analyze_game_code(), self.test_gameplay_mechanics(), self.evaluate_performance()]
        )

    @task
    def compile_qa_report(self) -> Task:
        return Task(
            config=self.tasks_config["compile_qa_report"],
            context=[
                self.analyze_game_code(),
                self.test_gameplay_mechanics(),
                self.evaluate_performance(),
                self.assess_user_experience(),
                self.identify_bugs()
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
