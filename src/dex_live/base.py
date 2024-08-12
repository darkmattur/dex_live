import abc
from os.path import isfile, dirname, join

from pathlib import Path
from glob import glob

import pandas as pd
import json
import yaml

import web3
import types


class ContractMeta(abc.ABCMeta):
    """
    Metaclass to handle post initialisation tasks
    """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__post_init__()
        return instance


class BaseContract(metaclass=ContractMeta):
    ADDRESS_ZERO = web3.constants.ADDRESS_ZERO
    daemon = True

    @property
    @abc.abstractmethod
    def abi(self):
        pass

    @property
    def address(self):
        return self._contract.address

    def __init__(self, chain, address):
        super(BaseContract, self).__init__()

        # Set contract base path
        self.conn = chain

        # Create web3 contract
        self._contract = self.conn.create_contract(address=address, abi=self.abi)

        # Add all function from ABI
        self.functions = types.SimpleNamespace()

        for f_def in self.abi:
            if f_def.get('type') != 'function':
                continue

            if f_def.get('stateMutability') == 'view':
                function = self._contract.functions.__dict__[f_def['name']]
                setattr(self.functions, f_def['name'], self._wrap_web3_function(function))

    def __post_init__(self):
        pass

    def update(self):
        """
        Update the cached data inside the class.
        """
        pass

    @staticmethod
    def clean_file_path(file_path):
        if isfile(file_path):
            file_path = dirname(file_path)
        return file_path

    @staticmethod
    def load_csv(file_path, *args):
        file_path = BaseContract._clean_file_path(file_path, *args)
        if not isfile(file_path): return None

        return pd.read_csv(file_path, index_col='index')

    @staticmethod
    def write_csv(dataframe, file_path, *args):
        file_path = BaseContract._clean_file_path(file_path, *args)
        return dataframe.to_csv(file_path, index_label='index')

    @staticmethod
    def load_json(file_path, *args):
        file_path = BaseContract._clean_file_path(file_path, *args)
        if not isfile(file_path): return None

        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def load_yml(file_path, *args):
        file_path = BaseContract._clean_file_path(file_path, *args)
        if not isfile(file_path): return None

        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def load_folder(folder_path, *args):
        folder_path = BaseContract._clean_file_path(folder_path, *args)

        json_files = {Path(folder_path).stem: BaseContract.load_json(json_path)
            for json_path in glob(join(folder_path, '*.json'))}
        yml_files = {Path(folder_path).stem: BaseContract.load_yml(yml_path)
            for yml_path in glob(join(folder_path, '*.yml'))}

        return dict(**yml_files, **json_files)

    @staticmethod
    def _clean_file_path(file_path, *args):
        if args:
            if isfile(file_path): file_path = dirname(file_path)
        return join(file_path, *args)

    @staticmethod
    def _wrap_web3_function(function):
        def wrapped_function(*args, **kwargs):
            return function(*args, **kwargs).call()
        return wrapped_function

    @staticmethod
    def check_address(address):
        return web3.Web3.is_checksum_address(address)
