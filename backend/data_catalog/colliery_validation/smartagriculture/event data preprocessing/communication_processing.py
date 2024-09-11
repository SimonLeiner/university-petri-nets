import os
import json
from csv import DictReader, DictWriter


mname = 'msgName'
mid = 'msgInstanceID'
commtype = 'msgRole'
commmode = 'msgProtocol'


def graph_handler(graph_dict):
    '''
    Generate an event log enriched with communication details
    @graph_dict: ROS nodes dependency graph
    '''
    out_list = []

    with open('MRS.csv') as csv_file:
        dict_reader = DictReader(csv_file)

        list_of_dict = list(dict_reader)

        out_list = []
        msg_count = 0

        last_msg = ''

        for ld in list_of_dict:
            time = ld.get('time')
            activity = ld.get('concept:name')
            resource = ld.get('org:group')

            if time in graph_dict.keys():

                node_dep = graph_dict.get(time)

                ld[commmode] = 'Pub/Sub'

                for el in node_dep:
                    if resource in el.get('node'):
                        if last_msg != activity or (last_msg == activity and el.get('communication') == 'pub'):
                            msg_count += 1
                        ld[mname] = activity.lower()
                        ld[commtype] = 'send' if el.get(
                            'communication') == 'pub' else 'receive'
                        ld[mid] = activity.lower() + '_' + str(msg_count)

                        last_msg = activity

            else:
                ld[commmode] = ''
                ld[mname] = ''
                ld[commtype] = ''
                ld[mid] = ''

            out_list.append(ld)

    header = list(out_list[0].keys())

    with open('MRS_coll.csv', 'w', newline='') as out_file:
        writer = DictWriter(out_file, fieldnames=header)

        writer.writeheader()
        writer.writerows(out_list)


if __name__ == "__main__":
    file = open(os.getcwd() + '/dependencies.json')
    graph_dict = json.load(file)

    graph = graph_handler(graph_dict)
