import collections
import logging
import os

import toml

from sawtooth_sdk.processor.exceptions import LocalConfigurationError

LOGGER = logging.getLogger(__name__)


# FIXME: xo
def load_default_coo_config():
    """
    Returns the default GDMConfig
    """
    return GDMConfig(
        connect='tcp://localhost:4004',
    )


# FIXME: xo
def load_toml_coo_config(filename):
    """Returns a GDMConfig created by loading a TOML file from the
    filesystem.

    Args:
        filename (string): The name of the file to load the config from

    Returns:
        config (GDMConfig): The GDMConfig created from the stored
            toml file.

    Raises:
        LocalConfigurationError
    """
    if not os.path.exists(filename):
        LOGGER.info(
            "Skipping transaction proccesor config loading from non-existent"
            " config file: %s", filename)
        return GDMConfig()

    LOGGER.info("Loading transaction processor information from config: %s",
                filename)

    try:
        with open(filename) as fd:
            raw_config = fd.read()
    except IOError as e:
        raise LocalConfigurationError(
            "Unable to load transaction processor configuration file:"
            " {}".format(str(e)))

    toml_config = toml.loads(raw_config)
    invalid_keys = set(toml_config.keys()).difference(
        ['connect'])
    if invalid_keys:
        raise LocalConfigurationError(
            "Invalid keys in transaction processor config: "
            "{}".format(", ".join(sorted(list(invalid_keys)))))

    config = GDMConfig(
        connect=toml_config.get("connect", None)
    )

    return config


def merge_coo_config(configs):
    """
    Given a list of GDMConfig objects, merges them into a single
    GDMConfig, giving priority in the order of the configs
    (first has highest priority).

    Args:
        config (list of GDMConfigs): The list of xo configs that
            must be merged together

    Returns:
        config (GDMConfig): One GDMConfig that combines all of the
            passed in configs.
    """
    connect = None

    for config in reversed(configs):
        if config.connect is not None:
            connect = config.connect

    return GDMConfig(
        connect=connect
    )


# FIXME: xo
class GDMConfig:
    def __init__(self, connect=None):
        self._connect = connect

    @property
    def connect(self):
        return self._connect

    def __repr__(self):
        return \
            "{}(connect={})".format(
                self.__class__.__name__,
                repr(self._connect),
            )

    def to_dict(self):
        return collections.OrderedDict([
            ('connect', self._connect),
        ])

    def to_toml_string(self):
        return str(toml.dumps(self.to_dict())).strip().split('\n')
