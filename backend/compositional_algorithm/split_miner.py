import subprocess


def split_miner(  # noqa: PLR0913
    input_log_path: str,
    output_path: str | None = None,
    epsilon: float | None = None,
    eta: float | None = None,
    use_splitminer2: bool = False,
    remove_loop_markers: bool = False,
    replace_iors: bool = False,
    parallelism_first: bool = False,
) -> str:
    # TODO: Path to the Split-Miner JAR file
    jar_path = "path/to/split-miner-1.5-all.jar"

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

    return result.stdout
