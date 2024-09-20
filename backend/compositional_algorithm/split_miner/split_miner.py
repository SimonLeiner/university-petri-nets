import subprocess
import os
import time
from pm4py import convert_to_petri_net, read_bpmn
from pathlib import Path
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet

def split_miner(  # noqa: PLR0913
    input_log_path: str,
    epsilon: float | None = None,
    eta: float | None = None,
    use_splitminer2: bool = True,
    remove_loop_markers: bool = False,
    replace_iors: bool = False,
    parallelism_first: bool = False,
) -> tuple[PetriNet, Marking, Marking]:
    """"
    Run the Split-Miner algorithm on the provided log file.
    
    Args:
        input_log_path: Path to the input log file.
        epsilon: The epsilon parameter for the algorithm.
        eta: The eta parameter for the algorithm.
        use_splitminer2: Whether to use Split-Miner 2.
        remove_loop_markers: Whether to remove loop markers.
        replace_iors: Whether to replace IORs.
        parallelism_first: Whether to use parallelism first.
    
    Comments:
        - https://github.com/iharsuvorau/split-miner?tab=readme-ov-file

    Returns:
        - A PetriNet object.
    """
    # Path to the Split-Miner JAR file
    jar_path = "/app/backend/compositional_algorithm/split_miner/split-miner-1.7.1-all.jar"

    # create output path from input path
    dir_name = os.path.dirname(input_log_path)
    base_name, _ = os.path.splitext(os.path.basename(input_log_path))
    new_base_name = base_name + "_split_mined.bpmn"
    output_path = os.path.join(dir_name, new_base_name)

    # Base command
    command = ["java", "-jar", jar_path]

    # Optional flags
    if use_splitminer2:
        command.append("-v2")
    if parallelism_first:
        command.append("-f")
    if remove_loop_markers:
        command.append("-l")
    if replace_iors:
        command.append("-r")
    if epsilon is not None:
        command.extend(["-p", str(epsilon)])
    if eta is not None:
        command.extend(["-e", str(eta)])

    # Add required input log path
    command.append(f"--logPath={input_log_path}")

    # Add optional output path if provided
    if output_path is not None:
        command.append(f"--outputPath={output_path}")

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        msg = f"Split-Miner failed with error: {result.stderr}"
        raise RuntimeError(msg)

    start_time = time.time()
    check_interval=2
    timeout = 20
    while True:
        if Path(output_path).exists():

            # read in npm file
            bpmn_model = read_bpmn(output_path)

            # convert bpmn model to petri net
            return convert_to_petri_net(bpmn_model)

        # no file found
        elif time.time() - start_time >= timeout:
            print(f"Timeout reached. File {output_path} not found.")
            raise FileNotFoundError(f"File {output_path} not found.")

        # wait x secs
        time.sleep(check_interval)
        
