import sys
import os
import pandas as pd

from llama_index.core.output_parsers import PydanticOutputParser
from typing import List, Optional, Literal
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, conint, confloat

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from helpers.helpers import read_json_to_str

class GRZ(BaseModel):
    value: Optional[float] = Field(
        None,
        description="Der numerische Wert der Grundflächenzahl oder 'null', falls nicht vorhanden.",
        example=0.75
    )

class GFZ(BaseModel):
    value: Optional[float] = Field(
        None,
        description="Der numerische Wert der Geschoßflächenzahl oder 'null', falls nicht vorhanden.",
        example=1.0
    )

class BuildingMetrics(BaseModel):
    
    grz: Optional[GRZ] = Field(None, description="Grundflächenzahl (GRZ)")
    
    gfz: Optional[GFZ] = Field(None, description="Geschoßflächenzahl (GFZ)")
    
class PromptRoleAndTask:
    """Describes LLM role and task for prompt."""

    role: str = "You are a helpful enviromental city planner. \n Based on the excerpt from a building plan provided below, we would like to extract following information.\n"

class PromptKpiDefinitions:
    """Provides definitions to each KPI in prompt."""

    definitions_string : str = read_json_to_str('./query/definitions.json')

@dataclass
class Llm_Extraction_Prompt:
    """
    The dataclass contains a prompt (=query text).
    Strategy: We make a single query to extract relevant info from BP.
    """

    """The dataclass contains a prompt (=query text) and a parser method for this prompt.
        Strategy: We make a single query to extract relevant info from BP.
"""

    role: Optional[str] = field(default=PromptRoleAndTask.role)
    KPIDefinitions: Optional[str] = field(default=PromptKpiDefinitions().definitions_string)
    #specifications: Optional[str] = field(default=prompt_specifications.specifications)

    def __init__(self, role=None, KPIDefinitions=None#, specifications=None
                 ):
        """Optional parameters allow default values to be loaded from a file if None is provided."""
        if role is None:
            role = PromptRoleAndTask.role  # Default role definition
        if KPIDefinitions is None:
            KPIDefinitions = PromptKpiDefinitions().definitions_string  # Default KPI definitions
#        if specifications is None:
#            specifications = prompt_specifications.specifications  # Default specifications

        self.query = f'{role}\n{KPIDefinitions}\n\
        Here is the excerpt: \n {{context_str}}'

        self.parser = PydanticOutputParser(output_cls=BuildingMetrics)

    def parse_gpt_output(self, gpt_question_output) -> pd.DataFrame:
        """Extract year, scope, value, and unit gpt_question_output using regular expressions."""

        building_metrics = self.parser.parse(gpt_question_output.message.content)

        #parsed_output = pd.DataFrame([entry.dict()
        #                             for entry in building_metrics.BuildingMetrics])

        return(building_metrics)
