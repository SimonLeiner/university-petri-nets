import logging
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import Response
from pm4py import read_xes
from pm4py import write_pnml
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the uploads directory exists
UPLOAD_DIR = "data_catalog/uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Ensure the downloads directory exists
DOWNLOAD_DIR = "data_catalog/downloads"
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to my API!"}


@app.post("/upload_file/", response_model=dict, status_code=201)
async def upload_file(file: UploadFile = File) -> dict:
    try:
        # Save the uploaded file to the server
        file_path = Path(UPLOAD_DIR) / file.filename
        with Path.open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while uploading the file. Please try again.",
        ) from e
    else:
        return {"file_path": file_path}


@app.post("/save_petrinet/", response_model=FileResponse, status_code=201)
async def save_model(
    petri_net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
) -> dict:
    try:
        # Define the file path to save the Petri net model
        file_path = Path(DOWNLOAD_DIR) / "model.pnml"

        # Write the Petri net to a .pnml file
        write_pnml(petri_net, initial_marking, final_marking, file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while downloading the model. Please try again.",
        ) from e
    else:
        # Return the file as a response
        return FileResponse(path=file_path)


@app.post("/save_image/")
async def save_image() -> dict:
    # TODO: download the model as svg. can be done with graphviz or some other library like plotly
    raise NotImplementedError


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
            algo_to_use = inductive_miner.apply  # noise_threshold=0.2
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
