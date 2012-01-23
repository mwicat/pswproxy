import yaml

def parse_rules(fname=None):
    rules = []
    for line in open(fname):
        line = line.rstrip('\n')
        if not (line == '' or line.startswith('#')):
            rules.append(line)
    return rules

class ConfigException(Exception):
    pass

class ConfigReader:

    def load(self, source):
        return {}

class YAMLConfigReader(ConfigReader):

    def load(self, source):
        return yaml.load(source)
