from pathlib import Path
from xml.dom import minidom


def determine_agent(ip_type: str, concept_name: str) -> list:  # noqa: C901
    """Determine the agent(s) responsible for a given concept name. Not working for IP-8."""
    if ip_type == "IP-1":
        ip_mapping_a1 = "a!"
    elif ip_type in ("IP-2", "IP-3"):
        ip_mapping_a1 = ("a!", "b!")
    elif ip_type == "IP-4":
        ip_mapping_a1 = ("a!", "b?")
    elif ip_type in ("IP-5", "IP-6"):
        ip_mapping_a1 = ("a!", "b!", "c?", "d?")
    elif ip_type == "IP-7":
        ip_mapping_a1 = ("a?", "b!", "c!")
    elif ip_type == "IP-8":
        msg = "IP-8 is not supported."
        raise NotImplementedError(msg)
    elif ip_type in ("IP-9", "IP-10", "IP-11", "IP-12"):
        ip_mapping_a1 = ("a!", "b?")

    # a/b/c/d -> Agent 1, Agent 2
    if concept_name.startswith(("a", "b", "c", "d")):
        if concept_name.startswith(ip_mapping_a1):
            return ["Agent 1"]
        return ["Agent 2"]

    # sync message for both agents -> Agent 1, Agent 2
    if concept_name.startswith("s"):
        return ["Agent 1", "Agent 2"]

    # t -> Agent 1 in log
    if concept_name.startswith("t"):
        return ["Agent 1"]

    # q/e (only in IP-1) -> Agent 2
    if concept_name.startswith("q"):
        return ["Agent 2"]
    return ["Unknown"]


def add_org_resource(ip_type: str, input_path: str, output_path: str) -> None:
    # Parse the XML file
    dom = minidom.parse(input_path)  # noqa: S318

    # Process each trace
    for trace in dom.getElementsByTagName("trace"):
        for event in trace.getElementsByTagName("event"):
            concept_name_elem = event.getElementsByTagName("string")
            for elem in concept_name_elem:
                if elem.getAttribute("key") == "concept:name":
                    concept_name = elem.getAttribute("value")
                    agents = determine_agent(ip_type, concept_name)

                    # Remove existing org:resource elements
                    for org_elem in event.getElementsByTagName("string"):
                        if org_elem.getAttribute("key") == "org:resource":
                            event.removeChild(org_elem)

                    # Add new org:resource elements
                    for agent in agents:
                        org_resource_elem = dom.createElement("string")
                        org_resource_elem.setAttribute("key", "org:resource")
                        org_resource_elem.setAttribute("value", agent)
                        event.appendChild(org_resource_elem)
                    break

    # Write the modified XML to the output file
    with Path.open(output_path, "w", encoding="utf-8") as f:
        # Split the XML string into lines
        xml_string = dom.toprettyxml(indent="\t")
        lines = xml_string.split("\n")

        # Remove empty lines and write to file
        non_empty_lines = [line for line in lines if line.strip()]
        f.write("\n".join(non_empty_lines))


# ip2
ip_type = "IP-2"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-2/IP2_initial_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-2_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip3
ip_type = "IP-3"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-3/IP-3_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-3_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip4
ip_type = "IP-4"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-4/IP-4_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-4_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip5
ip_type = "IP-5"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-5/IP-5_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-5_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip6
ip_type = "IP-6"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-6/IP-6_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-6_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip7
ip_type = "IP-7"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-7/IP-7_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-7_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip9
ip_type = "IP-9"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-9/IP-9_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-9_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip10
ip_type = "IP-10"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-10/IP-10_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-10_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip11
ip_type = "IP-11"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-11/IP-11_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-11_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)

# ip12
ip_type = "IP-12"
log_path = "/app/backend/data_catalog/compositional_process_discovery_experiment_data/IP-12/IP-12_init_log.xes"
output_path = "/app/backend/data_catalog/final_logs/IP-12_initial_log.xes"
add_org_resource(ip_type, log_path, output_path)
