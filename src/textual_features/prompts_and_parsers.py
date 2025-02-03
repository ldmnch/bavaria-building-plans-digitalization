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

class HW100(BaseModel):
    value: Optional[float] = Field(
        None,
        description="HW100 beschreibt den Hochwasserabfluss, der statistisch einmal in 100 Jahren zu erwarten ist.",
        example=315.40
    )

class HW10(BaseModel):
    value: Optional[float] = Field(
        None,
        description="HW10 beschreibt den Hochwasserabfluss, der statistisch einmal in 10 Jahren zu erwarten ist.",
        example=560.30
    )

class BuildingMetrics(BaseModel):
    
    grz: Optional[GRZ] = Field(None, description="Grundflächenzahl (GRZ)")
    
    gfz: Optional[GFZ] = Field(None, description="Geschoßflächenzahl (GFZ)")

class FloodingMetrics(BaseModel):

    hw100: Optional[HW100] = Field(None, description="Hochwasserabfluss HW100")
    
    hw10: Optional[HW10] = Field(None, description="Hochwasserabfluss HW10")
    
class PromptRoleAndTask:
    """Describes LLM role and task for prompt."""

    role: str = "You are a helpful enviromental city planner. \n Based on the excerpt from a building plan provided below, we would like to extract following information.\n"

class PromptKpiDefinitions:
    """Provides definitions to each KPI in prompt."""

    def __init__(self, path_to_definitions):
        self.path_to_definitions = path_to_definitions
        self.definitions_string : str = read_json_to_str(self.path_to_definitions)

@dataclass
class Llm_Extraction_Prompt:
    """
    The dataclass contains a prompt (=query text).
    Strategy: We make a single query to extract relevant info from BP.
    """
    role: Optional[str] = field(default=PromptRoleAndTask.role)
    #KPIDefinitions: Optional[str] = field(default=PromptKpiDefinitions().definitions_string)

    def __init__(self, role=None, prompt_type = 'construction'):
        
        """Optional parameters allow default values to be loaded from a file if None is provided."""
        if role is None:
            role = PromptRoleAndTask.role  # Default role definition
        if prompt_type == 'construction':
            KPIDefinitions = PromptKpiDefinitions(path_to_definitions = './query/construction_definitions.json').definitions_string  
            output_cls = BuildingMetrics
        if prompt_type == 'flooding':
            KPIDefinitions = PromptKpiDefinitions(path_to_definitions = './query/flooding_definitions.json').definitions_string
            output_cls = FloodingMetrics
        
        self.query = f'{role}\n{KPIDefinitions}\n\
        Here is the excerpt: \n {{context_str}}'

        self.parser = PydanticOutputParser(output_cls=output_cls)

    def parse_gpt_output(self, gpt_question_output) -> pd.DataFrame:
        """Extract year, scope, value, and unit gpt_question_output using regular expressions."""

        building_metrics = self.parser.parse(gpt_question_output.message.content)

        return(building_metrics)
