import base64
from openai import OpenAI
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
from crewai_tools import DallETool
from crewai.tools import BaseTool
import os
import re
import json
import pathlib
import requests
from typing import Any, List, Optional, Type

from bs4 import BeautifulSoup    
# ---------------------------------------------------------------------------
#  SaveDalleImageTool – generates + downloads image to ./assets/images/
# ---------------------------------------------------------------------------
import requests, os, pathlib, json, uuid
from typing import Any

# --------------------------- The actual Tool class ---------------------------
class GenerateAndDownloadImageSchema(BaseModel):
    prompt          : str = Field(..., description="Prompt for DALL·E")
    file_name       : str = Field(..., description="Where to save the image (PNG)")
    size            : str = Field("1024x1024", description="Image resolution")
    response_format : str = Field("url", description="url or b64_json")
    model           : str = Field("dall-e-3", description="DALL·E model name")
    n               : int = Field(1, description="Number of images (1)")

class GenerateAndDownloadImageTool(BaseTool):
    """
    A single tool that generates an image via OpenAI’s DALL·E API
    and downloads it locally (**url** or **b64_json** variant).
    """
    name        : str = "generate_and_download_image"
    description : str = (
        "Generate an image from a prompt via DALL·E, "
        "then download the resulting image to file."
    )
    args_schema : Type[BaseModel] = GenerateAndDownloadImageSchema

    # -------------------- sync entry‑point CrewAI will call ------------------
    def _run(self, **kwargs) -> Any:
        prompt          = kwargs["prompt"]
        file_name       = kwargs["file_name"]
        size            = kwargs.get("size", "1024x1024")
        response_format = kwargs.get("response_format", "url")
        model           = kwargs.get("model", "dall-e-3")
        n               = kwargs.get("n", 1)

        # -- Make sure OPENAI_API_KEY is set
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "OPENAI_API_KEY is not set in the environment."

        # -- Configure client
        client = OpenAI(api_key=openai_key)

        # -- Call DALL·E
        response = client.images.generate(
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format,
            model=model,
        )
        response_dict = response.model_dump(mode="python")

        if not response_dict or "data" not in response_dict or len(response_dict["data"]) == 0:
            return "No image data returned from DALL·E."

        # ---------------------------------------------------------
        # Depending on the response format, extract the image data
        # ---------------------------------------------------------
        if response_format == "url":
            image_url = response_dict["data"][0]["url"]

            # Download the image from the URL
            r = requests.get(image_url, timeout=30)
            r.raise_for_status()

            # Ensure folder exists
            pathlib.Path(file_name).expanduser().parent.mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(r.content)

            return json.dumps(
                {
                    "message": f"Image generated and saved as {file_name}.",
                    "url": image_url,
                },
                indent=2,
            )

        else:  # b64_json
            b64_data    = response_dict["data"][0]["b64_json"]
            image_bytes = b64_data.encode("utf-8")
            decoded     = base64.decodebytes(image_bytes)

            pathlib.Path(file_name).expanduser().parent.mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(decoded)

            return json.dumps(
                {
                    "message": f"Image generated (base64) and saved as {file_name}",
                },
                indent=2,
            )

    # async wrapper for CrewAI compliance
    async def _arun(self, **kwargs) -> Any:
        return self._run(**kwargs)
class SearchAndSaveSoundToolArgs(BaseModel):
    """Arguments accepted by SearchAndSaveSoundTool."""
    query: str = Field(..., description="Search text for the Freesound query")
    output_path: str = Field(
        ...,
        description="Absolute or relative path (including filename) where the preview will be written"
    )
    max_results: Optional[int] = Field(
        5,
        description="Maximum number of results to consider (the first hit will be downloaded)"
    )


class SearchAndSaveSoundTool(BaseTool):
    """
    Searches Freesound for the query, downloads the first preview,
    and returns metadata as a JSON string.
    """

    name: str = "search_and_save_sound"
    description: str = (
        "Search Freesound for an audio clip and save the first preview to disk. "
        "Returns a JSON blob describing the saved file."
    )
    args_schema = SearchAndSaveSoundToolArgs

    def __init__(self, freesound_client, **kwargs):
        """
        Parameters
        ----------
        freesound_client : freesound.FreesoundClient
            An authenticated Freesound client instance.
        """
        super().__init__(**kwargs)
        self.client = freesound_client

    # ---------- sync run ----------
    def _run(
        self,
        *,
        query: str,
        output_path: str,
        max_results: int = 5,
        **_
    ) -> Any:
        # ------------------------------------------------------------------ #
        # 1. Fetch search results                                             #
        # ------------------------------------------------------------------ #
        pager = self.client.text_search(
            query=query,
            sort="score",
            fields="id,name,username,previews",
            page_size=max_results,
        )
        results = list(pager[: max_results])

        if not results:
            return json.dumps({"error": "No results found."})

        chosen_sound = results[0]
        sound_id = chosen_sound.id
        sound_user = chosen_sound.username
        url = f"https://freesound.org/people/{sound_user}/sounds/{sound_id}/"

        # ------------------------------------------------------------------ #
        # 2. Scrape a short description                                       #
        # ------------------------------------------------------------------ #
        try:
            page = requests.get(url, timeout=10)
            page.raise_for_status()
            soup = BeautifulSoup(page.content, "html.parser")
            desc_section = soup.find(id="soundDescriptionSection")
            raw_desc = re.sub(r"<.*?>", "", str(desc_section)) if desc_section else ""
        except Exception:
            raw_desc = "N/A"

        # ------------------------------------------------------------------ #
        # 3. Save the preview locally                                         #
        # ------------------------------------------------------------------ #
        try:
            directory = os.path.dirname(output_path)
            filename = os.path.basename(output_path)

            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            chosen_sound.retrieve_preview(directory, filename)
        except Exception as e:
            return json.dumps(
                {
                    "error": f"Failed to save sound (ID={sound_id}): {e}"
                }
            )

        # ------------------------------------------------------------------ #
        # 4. Build & return response                                          #
        # ------------------------------------------------------------------ #
        response_data = {
            "chosen_sound_id": sound_id,
            "name": chosen_sound.name,
            "description": raw_desc.strip(),
            "saved_path": os.path.abspath(output_path),
        }
        return json.dumps(response_data, indent=2)

    # ---------- async run (CrewAI expects this wrapper) ----------
    async def _arun(self, **kwargs) -> Any:  # noqa: D401
        return self._run(**kwargs)

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
    @agent
    def image_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["image_generator"],
            tools=[GenerateAndDownloadImageTool()],   # 🟢 now saves files
            llm=self.llm,
        )
    @agent
    def audio_sourcer(self) -> Agent:
        """Fetches & normalises audio via the custom Freesound tool."""
        fs_tool = SearchAndSaveSoundTool()      # ← uses the code you supplied
        return Agent(
            config=self.agents_config["audio_sourcer"],
            tools=[fs_tool],
            llm=self.llm,
        )
    @agent
    def asset_integrator(self) -> Agent:
        """Agent that pipes finished assets into the codebase / repo."""
        return Agent(config=self.agents_config["asset_integrator"], llm=self.llm)

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
    @task
    def generate_visual_assets(self) -> Task:
        return Task(
            config=self.tasks_config["generate_visual_assets"],
            context=[self.analyze_asset_requirements()],
        )

    @task
    def source_audio_assets(self) -> Task:
        return Task(
            config=self.tasks_config["source_audio_assets"],
            context=[self.analyze_asset_requirements()],
        )

    @task
    def integrate_assets(self) -> Task:
        return Task(
            config=self.tasks_config["integrate_assets"],
            context=[
                self.generate_visual_assets(),
                self.source_audio_assets(),
                self.finalize_assets(),
            ],
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
