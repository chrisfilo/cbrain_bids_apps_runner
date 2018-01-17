from glob import glob
import json
import argparse
from bids.grabbids import BIDSLayout
from copy import deepcopy
from os.path import exists

def save_json(filename, subtask_dict):
    with open(filename, 'w') as fp:
        json.dump(subtask_dict, fp, indent=4, sort_keys=True)


def get_dep_ids(id_sources):
    dep_ids = []
    while id_sources:
        for id_source in id_sources:
            filename = glob(id_source)
            if filename and exists(filename[0]):
                with open(filename[0]) as fp:
                    dep_ids.append(fp.read().strip())
                id_sources.remove(id_source)
    return dep_ids


def prepare_and_save_subtask(tool_class, app_name, filename, invocation_dict, participant_label, analysis_level,
                             dep_ids):
    subtask_dict = {
        "tool-class": tool_class,
        "description": "A {} BIDS app submission".format(app_name),
        "share-wd-tid": "",
        "parameters": deepcopy(invocation_dict),
        "required-to-post-process": True
    }
    subtask_dict['parameters']['participant_label'] = participant_label
    subtask_dict['parameters']['analysis_level'] = analysis_level
    if dep_ids:
        subtask_dict['prerequisites'] = dep_ids
    print(subtask_dict)
    save_json(filename, subtask_dict)


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

    dep_ids = []
    for level in levels:
        id_sources = []

        if level.startswith('participant'):
            for participant in participants_to_analyze:
                filename = "subtask_%s_%s.json" % (level, participant)
                prepare_and_save_subtask(tool_class=args.app_descriptor_file,
                                         app_name=descriptor_dict['name'],
                                         filename=filename,
                                         invocation_dict=invocation_dict,
                                         participant_label=participant,
                                         analysis_level=level,
                                         dep_ids=dep_ids)
                id_sources.append(filename.replace('.json', '.*bid'))

            dep_ids = get_dep_ids(id_sources)

        elif level.startswith('group'):
            filename = "subtask_%s.json" % (level)
            prepare_and_save_subtask(tool_class=args.app_descriptor_file,
                                     app_name=descriptor_dict['name'],
                                     filename=filename,
                                     invocation_dict=invocation_dict,
                                     participant_label=participants_to_analyze,
                                     analysis_level=level,
                                     dep_ids=dep_ids)
            id_sources.append(filename.replace('.json', '.*bid'))
            dep_ids = get_dep_ids(id_sources)

