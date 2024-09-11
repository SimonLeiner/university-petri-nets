from pydantic import BaseModel
from pydantic.fields import Field


class InterfaceModel(BaseModel):
    name: str = Field(..., description="The name of the interface.")


class AlgorithmModel(BaseModel):
    name: str = Field(..., description="The algorithm to be applied.")
    parameters: dict | None = None  # Additional parameters for the algorithm
