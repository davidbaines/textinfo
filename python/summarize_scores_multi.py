#!/usr/bin/python
import argparse
from collections import deque
import csv
import datetime as dt
from natsort import natsorted
from operator import itemgetter
from pathlib import Path
from pprint import pprint
import re
import time
import yaml

csv.register_dialect("default")


def find_last_in_file(in_file, pattern, last_n=1):

    lastmatches = deque(maxlen=last_n)

    with open(in_file, "r", encoding="utf-8") as in_file:
        for line in in_file:
            match = re.match(pattern, line)
            if match:
                lastmatches.append(match)

    return lastmatches


def find_first_in_file(in_file, pattern, first_n=1):

    matches = []

    with open(in_file, "r", encoding="utf-8") as in_file:
        for line in in_file:
            match = re.match(pattern, line)
            if match:
                matches.append(match)
                if len(matches) >= first_n:
                    return matches

    return matches


def helper_function(infile, pattern, first_n=1):

    pattern = re.compile(pattern)
    result = find_first_in_file(infile, pattern, first_n)

    if result:
        return result[0].group(1)
    else:
        return None


def get_data_from_process_log(experiment, data):
    """ Useful data from preprocess log:
    trainer_interface.cc(458) LOG(INFO) all chars count=2067370
    trainer_interface.cc(479) LOG(INFO) Alphabet size=80
    trainer_interface.cc(480) LOG(INFO) Final character coverage=1
    trainer_interface.cc(512) LOG(INFO) Done! preprocessed 12899 sentences.
    unigram_model_trainer.cc(134) LOG(INFO) Making suffix array...
    unigram_model_trainer.cc(138) LOG(INFO) Extracting frequent sub strings...
    unigram_model_trainer.cc(189) LOG(INFO) Initialized 22602 seed sentencepieces
    trainer_interface.cc(518) LOG(INFO) Tokenizing input sentences with whitespace: 12899
    trainer_interface.cc(528) LOG(INFO) Done! 14756
    unigram_model_trainer.cc(484) LOG(INFO) Using 14756 sentences for EM training

    Near the end:
    INFO:tensorflow:Initialized source input layer:
    INFO:tensorflow: - vocabulary size: 4752
    INFO:tensorflow: - special tokens: BOS=no, EOS=no
    INFO:tensorflow:Initialized target input layer:
    INFO:tensorflow: - vocabulary size: 32000
    INFO:tensorflow: - special tokens: BOS=yes, EOS=yes

    """
    # Get data from the process log if it exists
    preprocess_log = experiment["folder"] / "preprocess.log"

    if preprocess_log.is_file() and preprocess_log.exists():

        re_tokens = re.compile(".*?num_tokens/piece=(\d*\.\d*)")
        tokens_per_pieces = find_last_in_file(preprocess_log, re_tokens, 1)
        for tokens_per_piece in tokens_per_pieces:
            print(tokens_per_piece[0])
        exit()

        if tokens_per_piece:
            experiment["tokens per piece"] = tokens_per_piece[0].group(1)
        else:
            experiment["tokens per piece"] = "Not found"

        for var, pattern in data.items():
            experiment[var] = helper_function(preprocess_log, pattern)

    return experiment


def get_data_from_log(experiment, log, patterns):

    # Get data from a log file.
    # Open log file, and search for the named groups in the patterns.
    # Add the data found to the experiment with the name as the key.

    if log.is_file() and log.exists():
        # print(f"Searching in {log}")
        for pattern in patterns:
            with open(log, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    match = re.match(pattern, line)
                    if match:
                        for named_group, data in match.groupdict().items():
                            experiment[named_group] = data

    return experiment


def get_config_data(config_file):
    # It is best to pass an effective config file to this function as it will gather
    # more data about the experiment. Passing a config.yml file will collect only
    # the explicit settings and not the defaults that were used.
    #    print(f"Reading {config_file}")

    experiment = {
        "config_file"  : str(config_file),
        "experiment" : config_file.parent.name,
        "folder"     : config_file.parent,
        "series"     : config_file.parent.parent.name,
        "complete"   : False,
        "score best" : 0,
        "score last" : 0,
    }
    git_commit = re.match("effective-config-(.*).yml", config_file.name)
    if git_commit:
        # print(f"Found git_commit : {git_commit, git_commit[0], git_commit[1]}")
        experiment["git_commit"] = git_commit[1]

    # print(f"Searching in {config_file}")

    with open(config_file, "r") as conf:
        config = yaml.load(conf, Loader=yaml.SafeLoader)

        if not "data" in config:
            # This probably isn't a config.yml file for one of our experiments.
            experiment["experiment"] = "Invalid - no data section"
            return experiment

    #    pairs = config["data"]["corpus_pairs"]
    #    for i, pair in enumerate(pairs):
    #        print(pair)
    #        experiment[f"corpus_pair_{i}"] = pair

    for value in [
        "parent",
        "parent_use_best",
        "parent_use_vocab",
        "src_vocab_size",
        "trg_vocab_size",
        "src_casing",
        "trg_casing",
        "mirror",
    ]:
        if value in config["data"]:
            experiment[value] = config["data"][value]
        else:
            experiment[value] = None

    # Add the terms settings to the experiment.
    # Typical terms are {'categories': 'PN', 'dictionary': False, 'include_glosses': True, 'train': False}
    # Any of keys that already exist in the experiment dict will be overwritten.

    if "terms" in config["data"]:
        experiment.update(config["data"]["terms"])
        # print(f"Terms are {terms}\n and is of type: {type(terms)}")

    if "params" in config:
        for value in [
            "coverage_penalty",
            "word_dropout",
            "guided_alignment_type",
            "guided_alignment_weight",
        ]:
            if value in config["params"]:
                experiment[value] = config["params"][value]
            else:
                experiment[value] = None

    return experiment


def write_csv(outfile, row_data, column_headers, mode="w"):
    """Write the data to a csv file. 
    """

    with open(outfile, mode, encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, restval="", extrasaction="ignore", fieldnames=column_headers
        )
        writer.writeheader()
        writer.writerows(row_data)

    return None


def show_progress(i, filecount, timestarted):

    ratio_done = i / filecount
    time_taken = time.time() - timestarted  # seconds
    rate = i / time_taken  # files per second
    if i == filecount:
        print(f"Read {filecount} files in {time_taken:.0f} seconds.")
    else:
        print(f"Read {i} files.\nElapsed time is {time_taken:.0f} seconds.")
        print(f"Estimated time remaining: {(filecount - i) / rate:.0f} seconds.")
    return None


def main() -> None:

    now = dt.datetime.now()
    timestarted = time.time()

    parser = argparse.ArgumentParser(
        description="Find and summarize SILNLP experiment scores. If both -c and -i are set neither will have an effect."
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more folders to search recursively for scores. The summary file is stored in a subfolder named results in the first folder.",
    )
    #    parser.add_argument("output", help="folder for summary csv file.")

    parser.add_argument(
        "-c",
        "-complete_only",
        action="store_true",
        help="Only report experiments which are complete and have a score file.",
    )
    parser.add_argument(
        "-i",
        "-incomplete_only",
        action="store_true",
        help="Only report experiments which are incomplete and do not have a score file.",
    )

    args = parser.parse_args()
    if args.c and args.i:
        args.c = False
        args.i = False

    experiment_paths = [Path(exp_path).resolve() for exp_path in args.folders]
    #    print(f"Found these experiment paths: {experiment_paths}")

    exp_root_len = 0

    output_path = experiment_paths[0] / "results"
    output_path.mkdir(exist_ok=True)

    scores_filename_prefix = r"scores-"
    ext = r".csv"

    re_steps = re.compile("scores-(\d*.000)\.csv")

    scores_file_pattern = "**/" + scores_filename_prefix + "*" + ext
    preprocess_log_pattern = "preprocess.log"
    train_log_pattern = "train.log"

    output_filename = f"scores_summary_{now.year}_{now.month}_{now.day}_{now.hour:02}h{now.minute:02}.csv"
    simple_output_filename = f"scores_summary.csv"
    output_file = output_path / output_filename
    missing_files = output_path / "missing_files.txt"

    # These are the fields in a scores file:
    # "book","src_iso", "trg_iso", "num_refs", "references", "sent_len", "scorer", "score"

    experiments = []
    files_missing = []
    effective_config_count = 0

    experiment_configs = []

    for experiment_path in experiment_paths:
        for config in experiment_path.rglob("config.yml"):
            if config.is_file():
                experiment_configs.append(config)

    total_configs = len(experiment_configs)
    # Remove duplicate paths (which can easily occur since multilple paths are given in the arguments.
    experiment_configs = list(dict.fromkeys(experiment_configs))
    print(
        f"Found {total_configs} configs initially, {len(experiment_configs)} are left after deduplication."
    )
    with open(r"C:\gutenberg\DCB_Prep\scripts\temp.log", "w", encoding="utf-8") as log:
    #with open("/home/david/scripts/temp.log", "w", encoding="utf-8") as log:
        log.writelines(
            [str(experiment_config) for experiment_config in experiment_configs]
        )

    for experiment_config in experiment_configs:
        experiment_folder = experiment_config.parent
        effective_configs = list(experiment_folder.glob("effective-config-*.yml"))

        if effective_configs:
            effective_config_count += 1
            experiment = get_config_data(effective_configs[0])

        else:  # Use the config.yml file
            experiment = get_config_data(experiment_config)

        # Get data from the process log if it exists
        preprocess_log = experiment["folder"] / "preprocess.log"
        preprocess_patterns = {
            "Git commit": ".*?INFO - Git commit: (.*)",
            "All chars count": ".*?LOG\(INFO\) all chars count=(.*)",
            "Alphabet size": ".*?LOG\(INFO\) Alphabet size=(.*)",
            "Vocabulary size": ".*?INFO:tensorflow: - vocabulary size: (.*)",
            "Alignment": ".*?INFO - Generating train alignments using (.*)",
            "Train size": ".*?INFO - train size: (\d*?), val size: \d*?, test size: \d*?, dict size: \d*?, terms train size: \d*?",
            "Val size": ".*?INFO - train size: \d*?, val size: (\d*?), test size: \d*?, dict size: \d*?, terms train size: \d*?",
            "Test size": ".*?INFO - train size: \d*?, val size: \d*?, test size: (\d*?), dict size: \d*?, terms train size: \d*?",
            "Dict size": ".*?INFO - train size: \d*?, val size: \d*?, test size: \d*?, dict size: (\d*?), terms train size: \d*?",
            "Terms train size": ".*?INFO - train size: \d*?, val size: \d*?, test size: \d*?, dict size: \d*?, terms train size: (\d*)",
        }

        preprocess_patterns = [
            ".*?INFO - Git commit: (?P<git_commit>.*)",
            ".*?LOG\(INFO\) all chars count=(?P<all_chars_count>.*)",
            ".*?LOG\(INFO\) Alphabet size=(?P<alphabet_size>.*)",
            ".*?INFO:tensorflow: - vocabulary size: (?P<vocabulary_size>.*)",
            ".*?INFO - Generating train alignments using (?P<alignment>.*)",
            ".*?INFO - train size: (?P<train_size>\d*?), val size: (?P<val_size>\d*?), test size: (?P<test_size>\d*?), dict size: (?P<dict_size>\d*?), terms train size: (?P<terms_train>\d*)",
            ".*?num_tokens/piece=(?P<tokens_per_piece>\d*\.\d*)",
        ]
        # Tokens per piece pattern relies of the code finding all references and storing only the last.

        preprocess_patterns = [re.compile(regex) for regex in preprocess_patterns]
        experiment = get_data_from_log(experiment, preprocess_log, preprocess_patterns)

        training_log = experiment["folder"] / "train.log"
        training_patterns = [
            re.compile(
                ".*?Evaluation result for step (?P<step>\d+): loss = (?P<loss>\d+.\d+) ; perplexity = (?P<perplexity>\d+.\d+) ; bleu = (?P<bleu>\d+.\d+)"
            )
        ]
        experiment = get_data_from_log(experiment, training_log, training_patterns)

        score_files = list(experiment["folder"].glob(scores_file_pattern))

        if len(score_files) > 0:
            scores = {}
            for score_file in experiment["folder"].glob(scores_file_pattern):
                #            print(i, score_file)

                m = re_steps.match(score_file.name)
                if m:
                    steps = int(m.group(1))
                    if score_file.is_file() and score_file.exists():
                        with open(score_file, "r", encoding="utf-8") as csvfile:
                            csvreader = csv.DictReader(csvfile, delimiter=",")
                            for row in csvreader:
                                if row["scorer"] == "BLEU":
                                    try:
                                        score, _ = row["score"].split("/", 1)
                                        score = float(score)
                                    except ValueError:
                                        print(row)
                                        exit()
                                    scores[steps] = score

            if len(scores) > 0:

                best_steps = min(scores.keys())
                last_steps = max(scores.keys())
                experiment["complete"] = True
                experiment["steps best"] = best_steps
                experiment["score best"] = scores[best_steps]
                experiment["steps last"] = last_steps
                experiment["score last"] = scores[last_steps]
                #                print(best_steps, scores[best_steps] , last_steps, scores[last_steps])

                experiment["score max"] = max(
                    experiment["score best"], experiment["score last"]
                )

        experiments.append(experiment)

        # If experiments without scores are being reported add them
        # This is useful for finding out the tokens/piece value of a series
        # Where only the preprocessing has been done.

    if args.c:
        include = [experiment for experiment in experiments if experiment["complete"]]
        print("Report includes only experiments with scores.")

        # In this case we should be able to sort by bleu scores. But might not want to.
        # include = sorted(include, key=lambda experiment: experiment["score max"])

    elif args.i:
        include = [
            experiment for experiment in experiments if not experiment["complete"]
        ]
        print("Report includes only experiments without scores..")

    else:
        print("Report includes all experiments.")
        include = experiments
        
    # Sort by config file.    
#    include = natsorted( experiments, key=lambda experiment: experiment["series"] + experiment["experiment"] )
    include = natsorted( include, key=lambda experiment: experiment["config_file"] )
    

    # Select here the order and name of fields for the summary file
    all_fieldnames = {
        "series"                 : "Series",
        "folder"                 : "Folder",
        "experiment"             : "Experiment",
        "complete"               : "Complete",
        "parent"                 : "Parent",
        "git_commit"             : "Git commit",
        "train_size"             : "Train size",
        "val_size"               : "Val size",
        "test_size"              : "Test size",
        # Typical terms are {'categories': 'PN', 'dictionary': False, 'include_glosses': True, 'train': False}
        "categories"             : "Term cats",
        "dictionary"             : "Create dict",
        "include_glosses"        : "include_glosses",
        "train"                  : "Train terms",
        "dict_size"              : "Dictionary",
        "terms_train"            : "Terms",
        "all_chars_count"        : "All Chars",
        "alphabet_size"          : "Alphabet",
        "vocabulary_size"        : "Parent Vocab",
        "src_casing"             : "Source case",
        "trg_casing"             : "Target case",
        "mirror"                 : "Mirror",
        "src_vocab_size"         : "Source vocab",
        "tokens_per_piece"       : "Tokens per piece",
        "trg_vocab_size"         : "Target vocab",
        "coverage_penalty"       : "Coverage",
        "word_dropout"           : "Dropout",
        "guided_alignment_type"  : "GA type",
        "guided_alignment_weight": "GA weight",
        "Alignment"              : "Alignment",
        "step"                   : "Last Train Steps",
        "loss"                   : "Loss last step",
        "perplexity"             : "Perplexity last step",
        "bleu"                   : "Bleu train last step", 
        "steps best"             : "Best Steps",
        "score best"             : "Best Bleu",
        "steps last"             : "Last Steps",
        "score last"             : "Last Bleu",
        "score max"              : "Max Bleu",
        "parent_use_best"        : "Parent use best",
        "parent_use_vocab"       : "Parent use vocab",
        "config_file"              : "Config file",

    }

    #    omit = ["Folder", "Parent", "Last Train Steps","Loss last step","Perplexity last step","Bleu train last step", "Alignment","Dropout","Coverage","Target vocab",]
    #    omit = ["Last Train Steps"]

    # With these omitted the output should be as before the Terms data was added.
    omit = [ "Last Train Steps", "Term cats", "Create dict", "include_glosses", "Train terms",  ]

    output_fields = [
        fieldname for fieldname in all_fieldnames.values() if fieldname not in omit
    ]

    #    experiment0 = experiments[0]
    #    pprint(experiment0)
    #    experiment0 = {fieldnames[k] if k in fieldnames else k:v for k,v in experiment0.items()}

    new_experiments = []
    for experiment in include:
        new_experiments.append(
            {
                all_fieldnames[k] if k in all_fieldnames else k: v
                for k, v in experiment.items()
            }
        )

    #    # Ensure that all the extra fieldnames are in the list of fieldnames.
    #    keys = fieldnames
    #    for experiment in experiments:
    #        for key in list(experiment):
    #            if key not in keys:
    #                keys.append(key)

    # print(f"The column headers for the csv file are: {output_fields}")

    #    exit()


    write_csv(output_file, new_experiments, output_fields)
    print(f"Wrote results for {len(new_experiments)} experiments to {output_file}")


if __name__ == "__main__":
    main()
# Example commandline
# python ~/scripts/summarize_scores_config_steps.py /home/david/gutenberg/MT/experiements/BT-English/Gela_AE
