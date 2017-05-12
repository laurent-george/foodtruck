import os
import yaml

config_file = os.path.join(os.path.dirname(__file__), 'config.yml')

with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
