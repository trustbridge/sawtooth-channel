import logging

from sawtooth_sdk.processor.exceptions import InvalidTransaction

LOGGER = logging.getLogger(__name__)


class GDMPayload:

    def __init__(self, payload):
        try:
            # The payload is csv utf-8 encoded string
            sender_ref, subject, predicate, object_, sender, receiver = payload.decode().split(",")  # noqa
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not sender_ref:
            raise InvalidTransaction('sender_ref is required')

        if '|' in sender_ref:
            raise InvalidTransaction('sender_ref cannot contain "|"')

        if not subject:
            raise InvalidTransaction('subject is required')

        if not predicate:
            raise InvalidTransaction('predicate is required')

        if not object_:
            raise InvalidTransaction('object_ is required')

        if not sender:
            raise InvalidTransaction('sender is required')

        if not receiver:
            raise InvalidTransaction('receiver is required')

        self._sender_ref = sender_ref
        self._subject = subject
        self._predicate = predicate
        self._object_ = object_
        self._sender = sender
        self._receiver = receiver

    @staticmethod
    def from_bytes(payload):
        return GDMPayload(payload=payload)

    @property
    def sender_ref(self):
        return self._sender_ref

    @property
    def subject(self):
        return self._subject

    @property
    def predicate(self):
        return self._predicate

    @property
    def object_(self):
        return self._object_

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver
