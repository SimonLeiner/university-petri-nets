import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from pm4py import fitness_alignments
from pm4py import precision_alignments
from pm4py import read_xes
from pm4py import write_pnml
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from compositional_algorithm.compositional_algorithm import compositional_discovery
from compositional_algorithm.interface_patterns.interface_patterns import (
    INTERFACE_PATTERNS,
)
from compositional_algorithm.split_miner.split_miner import split_miner
from compositional_algorithm.transformations.transformations import TRANSFORMATIONS
from entropy_conformance.entropy_conformance import entropy_conformance


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI instance
app = FastAPI()

# Load environment variables
frontend_url = os.getenv("REACT_FRONTEND_URL")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_url,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure Data Exists
DATA_DIR = "/app/backend/data_catalog"
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

# Ensure Data Exists
FINAL_DATA_DIR = "/app/backend/data_catalog/final_logs"
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

# Ensure Data Exists
TEMP_DATA_DIR = "/app/backend/data_catalog/temp_files"
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


@app.get("/")
async def read_root() -> JSONResponse:
    """Welcome message for the API"""
    return JSONResponse(content={"message": "Welcome to my API!"})


@app.post("/upload/")
async def upload_file(file: UploadFile = File) -> FileResponse:
    """Upload a file to the server"""
    try:
        # Save the uploaded file to the server
        file_path = Path(FINAL_DATA_DIR) / file.filename
        with Path.open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while uploading the file. Please try again.",
        ) from e
    else:
        return FileResponse(file_path)


@app.get("/files")
async def list_files() -> JSONResponse:
    """List all files in the data directory"""
    try:
        # List all files in the uploads directory that end with .xes
        files = [
            file.name
            for file in Path(FINAL_DATA_DIR).iterdir()
            if file.name.endswith(".xes")
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while listing the files. Please try again.",
        ) from e
    else:
        return JSONResponse(content={"files": files})


@app.get("/files/{filename}")
async def get_file(filename: str) -> FileResponse:
    """Download a file from the server"""
    try:
        file_path = Path(FINAL_DATA_DIR) / filename
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while downloading the file. Please try again.",
        ) from e
    else:
        return FileResponse(file_path)


@app.post("/discover/")
async def discover(
    file: UploadFile,
    algorithm_name: str = Form(...),
    interface_name: str = Form(...),
    noise_threshold: float = Form(...),
) -> dict:
    try:
        # get the file path
        input_log_path = Path(FINAL_DATA_DIR) / file.filename
        df_log = read_xes(input_log_path)

        # select wich algorithm to use
        if algorithm_name == "inductive":
            log_input = df_log
            algorithm = inductive_miner.apply
            algorithm_kwargs = {"noise_threshold": noise_threshold}
        elif algorithm_name == "split":
            log_input = input_log_path
            algorithm = split_miner
            algorithm_kwargs = {}

        # select the Interface pattern to use
        for inter in INTERFACE_PATTERNS:
            if inter.__name__ == interface_name:
                interface = inter
                break

        # Discover the process model
        result = await compositional_discovery(
            input_log_path=log_input,
            algorithm=algorithm,
            interface_pattern=interface,  # or also INTERFACE_PATTERNS for all possible
            transformations=TRANSFORMATIONS,
            agent_column="org:resource",
            algorithm_kwargs=algorithm_kwargs,
        )

        # extract the result
        net, initial_marking, final_marking = result

        # temporarily export to pnml
        temp_pnml_path = Path(TEMP_DATA_DIR) / "temp_net.pnml"
        pnml = write_pnml(net, initial_marking, final_marking, temp_pnml_path)

        # alignment based fitness and precision
        align_precision = fitness_alignments(
            df_log,
            net,
            initial_marking,
            final_marking,
        )
        align_fitness = precision_alignments(
            df_log,
            net,
            initial_marking,
            final_marking,
        )

        # entropy based fitness and precision
        entr_precision, entr_recall = entropy_conformance(
            input_log_path,
            temp_pnml_path,
        )

        # create the response
        response = {
            "net": pnml,
            "conformance": {
                "Alignment-based Fitness": align_fitness,
                "Alignment-based Precision": align_precision,
                "Entropy-based Fitness": entr_precision,
                "Entropy-based Precision": entr_recall,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred during process discovery.",
        ) from e
    else:
        return Response(content=json.dumps(response), media_type="application/xml")
