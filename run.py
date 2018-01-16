from glob import glob
import json
import argparse
from bids.grabbids import BIDSLayout
from copy import deepcopy

from os.path import exists


def save_json(filename):
    with open(filename, 'w') as fp:
        json.dump(subtask_dict, fp, indent=4, sort_keys=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example BIDS App entrypoint script.')
    parser.add_argument('app_descriptor_file', help='app descriptor')
    parser.add_argument('invocation_file', help='invocation file')

    args = parser.parse_args()

    descriptor_dict = json.load(open(args.app_descriptor_file))

    levels = None
    for input in descriptor_dict['inputs']:
        if input['id'] == 'analysis_level':
            levels = input['value-choices']
    assert levels, "analysis_level must have value-choices"

    invocation_dict = json.load(open(args.invocation_file))

    bids_dir = invocation_dict['bids_dir']

    layout = BIDSLayout(bids_dir)
    participants_to_analyze = []
    if 'participant_label' in invocation_dict.keys():
        participants_to_analyze = invocation_dict['participant_label']
    # for all subjects
    else:
        participants_to_analyze = layout.get_subjects()

    print(levels)
    print(participants_to_analyze)

    subtask_template_dict = {
        "tool-class": args.app_descriptor_file,
        "description": "A {} BIDS app submission".format(descriptor_dict['name']),
        "share-wd-tid": "",
        "parameters": {
            "analysis_level": "",
            "participant_label": ""
        },
        "required-to-post-process": True
    }

    ids = []
    for level in levels:
        if level.startswith('participant'):
            id_sources = []
            for participant in participants_to_analyze:
                subtask_dict = deepcopy(subtask_template_dict)
                subtask_dict['parameters'] = deepcopy(invocation_dict)
                subtask_dict['parameters']['participant_label'] = participant
                subtask_dict['parameters']['analysis_level'] = level
                print(subtask_dict)
                filename = "subtask_%s_%s.json"%(level, participant)
                save_json(filename)
                id_sources.append(filename.replace('.json', '.*bid'))

            while id_sources:
                for id_source in id_sources:
                    filename = glob(id_source)
                    if filename and exists(filename[0]):
                        with open(filename[0]) as fp:
                            ids.append(fp.read().strip())
                        id_sources.remove(id_source)

        elif level.startswith('group'):
            subtask_dict = deepcopy(subtask_template_dict)
            subtask_dict['parameters'] = deepcopy(invocation_dict)
            subtask_dict['parameters']['participant_label'] = participants_to_analyze
            subtask_dict['parameters']['analysis_level'] = level
            subtask_dict['prerequisites'] = ids
            print(subtask_dict)
            filename = "subtask_%s.json" % (level)
            save_json(filename)
            ids = []
