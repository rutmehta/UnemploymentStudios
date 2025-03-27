from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import Pydantic Types
from unemploymentstudios.types import TestTypes

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class TestCrew:
    """Test Crew"""
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



    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------



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
        