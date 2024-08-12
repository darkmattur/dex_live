from os import path, environ

import yaml
from pathlib import Path
from glob import glob

config = {Path(file).stem: yaml.safe_load(open(file, 'r'))
          for file in glob(path.join(environ["CRYPTO"], '*.yml'))}
if not config:
    raise EnvironmentError(f'Unable to find configuration for dex_live!')
