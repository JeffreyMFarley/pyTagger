from configargparse import getArgumentParser

gp = getArgumentParser(
    default_config_files=['./config.ini'],
    args_for_setting_config_path=['--config'],
    args_for_writing_out_config_file=['--save-config']
)

from pyTagger.proxies.es import Client
from pyTagger.proxies.echonest import EchoNestProxy

if __name__ == "__main__":
    args = gp.parse()
    print(args)
