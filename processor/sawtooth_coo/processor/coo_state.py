import hashlib

from sawtooth_sdk.processor.exceptions import InternalError


GDM_NAMESPACE = hashlib.sha512('generic-discrete-message'.encode("utf-8")).hexdigest()[0:6]


#TODO: fix address construction
def _make_coo_address(sender_ref):
    return GDM_NAMESPACE + \
        hashlib.sha512(sender_ref.encode('utf-8')).hexdigest()[:64]


class Message:
    def __init__(self, sender_ref, subject, predicate, object_, sender, receiver):
        self.sender_ref = sender_ref
        self.subject = subject
        self.predicate = predicate
        self.object = object_
        self.sender = sender
        self.receiver = receiver


class GDMState:

    TIMEOUT = 3

    def __init__(self, context):
        """Constructor.

        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
        """

        self._context = context
        self._address_cache = {}

    # TODO: do we need to be able to delete messages?
    # def delete_certificate(self, certificate_name):
    #     """Delete the Certificate named certificate_name from state.

    #     Args:
    #         certificate_name (str): The name.

    #     Raises:
    #         KeyError: The Certificate with certificate_name does not exist.
    #     """

    #     certificates = self._load_certificates(
    #         certificate_name=certificate_name)

    #     del certificates[certificate_name]
    #     if certificates:
    #         self._store_certificate(
    #             certificate_name, certificates=certificates)
    #     else:
    #         self._delete_certificate(certificate_name)

    def set_message(self, message):
        """Store the certificate in the validator state.

        Args:
            certificate_name (str): The name.
            certificate (Certificate): info specifying the current certificate.
        """
        sender_ref = message.sender_ref
        messages = self._load_messages(sender_ref=sender_ref)

        messages[sender_ref] = message

        self._store_message(sender_ref, messages=messages)

    def get_message(self, sender_ref):
        """Get the certificate associated with certificate_name.

        Args:
            certificate_name (str): The name.

        Returns:
            (Certificate): All the information specifying a certificate.
        """

        return self._load_messages(sender_ref=sender_ref).get(sender_ref)

    def _store_message(self, sender_ref, messages):
        address = _make_coo_address(sender_ref)

        state_data = self._serialize(messages)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _delete_certificate(self, certificate_name):
        address = _make_coo_address(certificate_name)

        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)

        self._address_cache[address] = None

    def _load_messages(self, sender_ref):
        address = _make_coo_address(sender_ref)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_messages = self._address_cache[address]
                messages = self._deserialize(serialized_messages)
            else:
                messages = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                messages = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                messages = {}

        return messages

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python
        Certificate objects.

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): certificate name (str) keys, Certificate values.
        """

        messages = {}
        try:
            for message in data.decode().split('|'):
                sender_ref, subject, object_, predicate, sender, receiver = message.split(',')  # noqa

                messages[sender_ref] = Message(sender_ref,
                                               subject,
                                               object_,
                                               predicate,
                                               sender,
                                               receiver)
        except ValueError:
            raise InternalError('Failed to deserialize message data')

        return messages

    def _serialize(self, messages):
        """Takes a dict of certificate objects and serializes them into bytes.

        Args:
            certificates (dict): certificate name (str) keys, Certificate values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        message_strs = []
        for sender_ref, g in messages.items():
            message_str = ','.join(
                [
                    sender_ref,
                    g.subject,
                    g.object,
                    g.predicate,
                    g.sender,
                    g.receiver
                ])
            message_strs.append(message_str)

        return '|'.join(sorted(message_strs)).encode()
