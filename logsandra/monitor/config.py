# Global import
import yaml

def parse(config_file):
    file_handler = open(config_file)
    return yaml.load(file_handler.read())
