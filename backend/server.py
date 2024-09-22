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
from pm4py import discover_petri_net_inductive
from pm4py import read_xes
from pm4py import write_pnml

# from compositional_algorithm.compositional_algorithm import compositional_discovery
from compositional_algorithm.compositional_algorithm import discover as discover_temp
from compositional_algorithm.interface_patterns.interface_patterns import (
    INTERFACE_PATTERNS,
)
from compositional_algorithm.split_miner.split_miner import split_miner


# from compositional_algorithm.transformations.transformations import TRANSFORMATIONS


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
    noise_threshold: float | None = Form(...),
) -> dict:
    try:
        # get the file path
        input_log_path = str(Path(FINAL_DATA_DIR) / file.filename)
        df_log = read_xes(input_log_path)

        # select wich algorithm to use
        if algorithm_name == "inductive":
            algorithm = discover_petri_net_inductive
            algorithm_kwargs = {"noise_threshold": noise_threshold}
        elif algorithm_name == "split":
            algorithm = split_miner
            algorithm_kwargs = {}

        # select the Interface pattern to use
        for inter in INTERFACE_PATTERNS:
            if inter.name == interface_name:
                interface = inter
                break

        # TODO: # Discover the process model
        # net, initial_marking, final_marking = await compositional_discovery(
        #     input_log_path=input_log_path,
        #     algorithm=algorithm,
        #     interface_pattern=interface,  # or also INTERFACE_PATTERNS for all possible
        #     transformations=TRANSFORMATIONS,
        #     agent_column="org:resource",
        #     **algorithm_kwargs=algorithm_kwargs,
        # )

        # TODO: remove this
        net, initial_marking, final_marking = discover_temp(
            input_log_path,
            discover_petri_net_inductive,
            **algorithm_kwargs,
        )

        # temporarily export to pnml
        temp_pnml_path = Path(TEMP_DATA_DIR) / "temp_net.pnml"
        write_pnml(net, initial_marking, final_marking, temp_pnml_path)

        # TODO: # alignment based fitness and precision
        # align_precision = fitness_alignments(
        #     df_log,
        #     net,
        #     initial_marking,
        #     final_marking,
        # )
        # align_fitness = precision_alignments(
        #     df_log,
        #     net,
        #     initial_marking,
        #     final_marking,
        # )

        # # entropy based fitness and precision
        # entr_precision, entr_recall = entropy_conformance(
        #     input_log_path,
        #     temp_pnml_path,
        # )

        # TODO: remove this
        align_precision = 1
        align_fitness = 1
        entr_precision = 1
        entr_recall = 1

        # can't go from Petri net to json directly
        with Path.open(temp_pnml_path, "r") as pnml_file:
            pnml_content = pnml_file.read()

        # remove temp file
        # if Path.exists(temp_pnml_path):
        #     Path(temp_pnml_path).unlink()

        # create the response
        response = {
            "pnml_content": pnml_content,
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
            detail=f"An error occurred during process discovery. {e}",
        ) from e
    else:
        return Response(content=json.dumps(response), media_type="application/xml")
