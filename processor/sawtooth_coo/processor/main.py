import sys
import os
import argparse
import pkg_resources

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.config import get_log_dir
from sawtooth_sdk.processor.config import get_config_dir
from sawtooth_coo.processor.handler import CoOTransactionHandler
from sawtooth_coo.processor.config.xo import XOConfig
from sawtooth_coo.processor.config.xo import \
    load_default_coo_config
from sawtooth_coo.processor.config.xo import \
    load_toml_coo_config
from sawtooth_coo.processor.config.xo import \
    merge_coo_config


DISTRIBUTION_NAME = 'sawtooth-coo'


def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-C', '--connect',
        help='Endpoint for the validator connection')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase output sent to stderr')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='print version information')

    return parser.parse_args(args)


def load_coo_config(first_config):
    default_coo_config = \
        load_default_coo_config()
    # FIXME: why is the config file called xo.toml?
    conf_file = os.path.join(get_config_dir(), 'xo.toml')

    toml_config = load_toml_coo_config(conf_file)

    return merge_coo_config(
        configs=[first_config, toml_config, default_coo_config])


def create_coo_config(args):
    # FIXME: rename this class
    return XOConfig(connect=args.connect)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        arg_config = create_coo_config(opts)
        xo_config = load_coo_config(arg_config)  # FIXME: phrasing!
        processor = TransactionProcessor(url=xo_config.connect)
        log_config = get_log_config(filename="xo_log_config.toml")  # FIXME

        # If no toml, try loading yaml
        # FIXME: xo_...
        if log_config is None:
            log_config = get_log_config(filename="xo_log_config.yaml")

        if log_config is not None:
            log_configuration(log_config=log_config)
        else:
            log_dir = get_log_dir()
            # use the transaction processor zmq identity for filename
            log_configuration(
                log_dir=log_dir,
                name="xo-" + str(processor.zmq_id)[2:-1])  # FIXME; xo-...

        init_console_logging(verbose_level=opts.verbose)

        handler = CoOTransactionHandler()

        processor.add_handler(handler)

        processor.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e))
    finally:
        if processor is not None:
            processor.stop()
