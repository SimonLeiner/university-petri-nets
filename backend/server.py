import logging
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pm4py import read_xes
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from compositional_algorithm.compositional_algorithm import compositional_discovery
from compositional_algorithm.interface_patterns.interface_patterns import (
    INTERFACE_PATTERNS,
)
from compositional_algorithm.transformations.transformations import TRANSFORMATIONS
from models import AlgorithmModel
from models import InterfaceModel


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI instance
app = FastAPI()

# Load environment variables
backend_server_url = os.getenv("PYTHON_BACKEND_URL")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[backend_server_url],  # Allow your React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific HTTP methods if needed
    allow_headers=["*"],  # You can specify specific headers if needed
)

# Ensure the uploads directory exists
UPLOAD_DIR = "data_catalog/uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.post("/discover/")
async def discover_process(
    file: UploadFile,
    algorithm_choice: AlgorithmModel,
    interface_choice: InterfaceModel,
) -> dict:
    try:
        # Upload the log file to the server and convert into a PM4Py log
        file_content = await file.read()
        df_log = read_xes(BytesIO(file_content))

        # select wich algorithm to use
        algo_name = algorithm_choice
        if algo_name == "inductive":
            algo_to_use = inductive_miner.apply # noise_threshold=0.2
        # TODO: implement split miner
        elif algo_name == "split":
            algo_to_use = "split_miner"

        # select the Interface pattern to use
        interface_name = interface_choice.name.upper()
        for interface in INTERFACE_PATTERNS:
            if interface.__name__ == interface_name:
                interface_to_use = interface
                break

        # Discover the process model
        model = await compositional_discovery(
            df_log=df_log,
            algorithm=algo_to_use,
            interface_pattern=interface_to_use,  # or also INTERFACE_PATTERNS for all possible
            transformations=TRANSFORMATIONS,
            agent_column="org:resource",
            algorithm_kwargs=algorithm_choice.parameters,  # Don't have to be specified for split miner
        )

        # return a reponse
        return Response(content=model, media_type="application/xml")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred during process discovery.",
        ) from e
