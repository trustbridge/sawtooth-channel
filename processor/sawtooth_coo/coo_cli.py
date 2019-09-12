from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

# FIXME: we reffer to CooClient but import GDMClient?
from sawtooth_coo.coo_client import GDMClient
from sawtooth_coo.coo_exceptions import CoOException


DISTRIBUTION_NAME = 'sawtooth-gdm'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def add_send_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'send',
        help='sends a new generic message',
        description='Sends a transaction to create a new message with the '
        'identifier <sender_ref>. This transaction will fail if the specified '
        'message already exists.',
        parents=[parent_parser])

    parser.add_argument(
        'sender_ref',
        type=str,
        help='unique identifier for the new message')

    parser.add_argument(
        'subject',
        type=str,
        help='the subject of the new message')

    parser.add_argument(
        'predicate',
        type=str,
        help='the predicate of the new message')

    parser.add_argument(
        'object',
        type=str,
        help='the object of the new message')

    parser.add_argument(
        'sender',
        type=str,
        help='sender of the message')

    parser.add_argument(
        'receiver',
        type=str,
        help='receiver of the message')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of sender's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for certificate to commit')


##############################################################
# FIXME: this looks like boilerplate from the XO sample game #
# TODO: delete it if not required, else fix it               #
##############################################################
def add_list_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'list',
        help='TODO: write help here FIXME:',
        description='TODO: write a description FIXME:',
        parents=[parent_parser])

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')


def add_show_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'show',
        help='Displays information about an xo certificate',
        description='Displays the xo certificate <name>, showing the players, '
        'the certificate state, and the board',
        parents=[parent_parser])

    parser.add_argument(
        'certificate_number',
        type=str,
        help='identifier for the document')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='TODO: FIXME: describe the create parser',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_send_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)

    return parser


def do_list(args):
    url = _get_url(args)
    auth_user, auth_password = _get_auth_info(args)

    client = GDMClient(base_url=url, keyfile=None)

    certificate_list = [
        certificate.split(',')
        for certificates in client.list(
                auth_user=auth_user,
                auth_password=auth_password)
        for certificate in certificates.decode().split('|')
    ]

    if certificate_list is not None:
        fmt = "%-15s %-15.15s %-15.15s %s"
        print(fmt % ('DOCUMENT_HASH', 'SENDER', 'RECIPIENT', 'STATE'))
        for certificate_data in certificate_list:

            certificate_number, status, sender, recipient = certificate_data

            print(fmt % (certificate_number, sender[:6], recipient[:6], status))
    else:
        # FIXME: rename CoOException to GDMException
        raise CoOException("Could not retrieve certificate listing.")


def do_send(args):
    sender_ref = args.sender_ref
    subject = args.subject
    predicate = args.predicate
    object_ = args.object
    sender = args.sender
    receiver = args.receiver

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = GDMClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create(
            sender_ref, subject, predicate, object_, sender, receiver,
            wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create(
            sender_ref, subject, predicate, object_, sender, receiver,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))


def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
    sender = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, sender)


def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'send':
        do_send(args)
    elif args.command == 'list':
        do_list(args)
    else:
        raise CoOException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except CoOException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
