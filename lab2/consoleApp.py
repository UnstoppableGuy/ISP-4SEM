import argparse
import configparser
import os

path = os.getcwd()


def parser_build():
    parser = argparse.ArgumentParser(
        description="Output format , input and output files")
    parser.add_argument('--output_format', type=str,
                        default="json", help=" output format")
    parser.add_argument('--input_file', type=str,
                        default=f"{path}/config.pickle",
                        help="input file")
    parser.add_argument('--output_file', type=str,
                        default=f"{path}/config.json",
                        help="output file")
    parser.add_argument('--config', type=str, help="path to config file")
    return parser


def read_from_config(path_to_config):
    config = configparser.ConfigParser()
    config.read(path_to_config)
    default_values = {'output_format': "json",
                      'input_file': f"{path}/config.json",
                      'output_file': f"{path}/config.toml"}
    value = [config.get("Parameters", "output_format"), config.get("Parameters", "input_file"),
             config.get("Parameters", "output_file")]
    default_values['output_format'] = value[0]
    default_values['input_file'] = value[1]
    default_values['output_file'] = value[2]
    return default_values
