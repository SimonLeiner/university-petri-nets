import subprocess


def entropy_conformance(
    input_log_path: str,
    input_model_path: str,
) -> tuple[float, float]:
    """
    Run the jbpt-pm-entropia tool with the provided options.

    Args:
        input_log_path: Path to the input log file.
        input_model_path: Path to the input model file.

    Comments:
        - https://github.com/jbpt/codebase/blob/master/jbpt-pm/entropia/guide.pdf
        - entropy_type: Entropy measure to compute. One of emp(exact matching precision) or empr (exact matching recall) or empr for both.
        - java -jar jbpt-pm-entropia -1.5.jar -emp -rel=log.xes -ret=model.pnml

    """
    # Path to the jbpt-pm-entropia JAR file
    jar_path = "/app/backend/entropy_conformance/jbpt-pm-entropia-1.7.jar"

    # Base command
    command = [
        "java",
        "-jar",
        jar_path,
        "-empr",
        "-s",
        f"-rel={input_log_path}",
        f"-ret={input_model_path}",
    ]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        msg = f"Entropy computation failed with error: {result.stderr}"
        raise RuntimeError(msg)

    return map(float, result.stdout.split(","))
