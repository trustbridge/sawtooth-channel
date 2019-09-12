"""
FIXME: this code needs unit tests,
so the copy-pasta can be removed.
"""
import logging


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

from sawtooth_coo.processor.coo_payload import GDMPayload
from sawtooth_coo.processor.coo_state import Message
from sawtooth_coo.processor.coo_state import GDMState
from sawtooth_coo.processor.coo_state import GDM_NAMESPACE


LOGGER = logging.getLogger(__name__)


class CoOTransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return 'generic-discrete-message'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [GDM_NAMESPACE]

    def apply(self, transaction, context):

        header = transaction.header
        signer = header.signer_public_key

        coo_payload = GDMPayload.from_bytes(transaction.payload)

        coo_state = GDMState(context)

        # if coo_payload.action == 'delete':
        #     certificate = coo_state.get_certificate(coo_payload.name)

        #     if certificate is None:
        #         raise InvalidTransaction(
        #             'Invalid action: certificate does not exist')

        #     coo_state.delete_certificate(coo_payload.name)

    # elif coo_payload.action == 'create':
        LOGGER.info(coo_payload.sender_ref)

        if coo_state.get_message(coo_payload.sender_ref) is not None:
            raise InvalidTransaction(
                'Invalid action: Message already exists: {}'.format(
                    coo_payload.sender_ref))

        message = Message(sender_ref=coo_payload.sender_ref,
                          subject=coo_payload.subject,
                          predicate=coo_payload.predicate,
                          object_=coo_payload.object_,
                          sender=coo_payload.sender,
                          receiver=coo_payload.receiver)

        coo_state.set_message(message)
        _display("User {} created a certificate.".format(signer[:6]))

        # elif coo_payload.action == 'acquit':
        #     certificate = coo_state.get_certificate(
        #         coo_payload.certificate_number)

        #     if certificate is None:
        #         raise InvalidTransaction(
        #             'Invalid action: Take requires an existing certificate')

        #     if certificate.status in ('cancelled', 'expired', 'acquitted'):
        #         raise InvalidTransaction(
        #             'Invalid Action: Certificate already acquitted')

        # fix this...
        # if (certificate.recipient != signer):
        #     raise InvalidTransaction(
        #         "Only recipient can acquit: {}".format(signer[:6]))

        # certificate.status = 'acquitted'

        # coo_state.set_certificate(
        #     coo_payload.certificate_number, certificate)
        # _display(
        #     "User {} takes space: {}\n\n".format(
        #         signer[:6],
        #         coo_payload.space)
        #     + _certificate_data_to_str(
        #         certificate.board,
        #         certificate.state,
        #         certificate.player1,
        #         certificate.player2,
        #         coo_payload.name))

        # else:
        #     raise InvalidTransaction('Unhandled action: {}'.format(
        #         coo_payload.action))


# FIXME: remove the copy-pasta!
def _update_board(board, space, state):
    if state == 'P1-NEXT':
        mark = 'X'
    elif state == 'P2-NEXT':
        mark = 'O'

    index = space - 1

    # replace the index-th space with mark, leave everything else the same
    return ''.join([
        current if square != index else mark
        for square, current in enumerate(board)
    ])


def _update_certificate_state(certificate_state, board):
    x_wins = _is_win(board, 'X')
    o_wins = _is_win(board, 'O')

    if x_wins and o_wins:
        raise InternalError('Two winners (there can be only one)')

    elif x_wins:
        return 'P1-WIN'

    elif o_wins:
        return 'P2-WIN'

    elif '-' not in board:
        return 'TIE'

    elif certificate_state == 'P1-NEXT':
        return 'P2-NEXT'

    elif certificate_state == 'P2-NEXT':
        return 'P1-NEXT'

    elif certificate_state in ('P1-WINS', 'P2-WINS', 'TIE'):
        return certificate_state

    else:
        raise InternalError('Unhandled state: {}'.format(certificate_state))


def _is_win(board, letter):
    wins = ((1, 2, 3), (4, 5, 6), (7, 8, 9),
            (1, 4, 7), (2, 5, 8), (3, 6, 9),
            (1, 5, 9), (3, 5, 7))

    for win in wins:
        if (board[win[0] - 1] == letter
                and board[win[1] - 1] == letter
                and board[win[2] - 1] == letter):
            return True
    return False


def _certificate_data_to_str(board, certificate_state, player1, player2, name):
    board = list(board.replace("-", " "))
    out = ""
    out += "GAME: {}\n".format(name)
    out += "PLAYER 1: {}\n".format(player1[:6])
    out += "PLAYER 2: {}\n".format(player2[:6])
    out += "STATE: {}\n".format(certificate_state)
    out += "\n"
    out += "{} | {} | {}\n".format(board[0], board[1], board[2])
    out += "---|---|---\n"
    out += "{} | {} | {}\n".format(board[3], board[4], board[5])
    out += "---|---|---\n"
    out += "{} | {} | {}".format(board[6], board[7], board[8])
    return out


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    # pylint: disable=logging-not-lazy
    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")
