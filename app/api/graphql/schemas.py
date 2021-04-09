import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from substrateinterface.utils.ss58 import ss58_encode
from app.models.explorer import Block, Extrinsic, Event
from app.models.runtime import Runtime, RuntimeCall, RuntimeCallArgument, RuntimeConstant, RuntimeErrorMessage, \
    RuntimeEvent, RuntimeEventAttribute, RuntimePallet, RuntimeStorage, RuntimeType


class BlockSchema(SQLAlchemyObjectType):
    number = graphene.Int()

    class Meta:
        model = Block


class ExtrinsicSchema(SQLAlchemyObjectType):
    multi_address_account_id = graphene.String()
    block_number = graphene.Int()

    def resolve_multi_address_account_id(self, info):
        return ss58_encode(self.multi_address_account_id)

    class Meta:
        model = Extrinsic


class EventSchema(SQLAlchemyObjectType):
    block_number = graphene.Int()

    class Meta:
        model = Event


class RuntimeSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = Runtime


class RuntimeCallSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeCall


class RuntimeCallArgumentSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()
    call_argument_idx = graphene.Int()

    class Meta:
        model = RuntimeCallArgument


class RuntimeConstantSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()
    pallet_constant_idx = graphene.Int()

    class Meta:
        model = RuntimeConstant


class RuntimeErrorMessageSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeErrorMessage


class RuntimeEventSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeEvent


class RuntimeEventAttributeSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeEventAttribute


class RuntimePalletSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimePallet


class RuntimeStorageSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeStorage


class RuntimeTypeSchema(SQLAlchemyObjectType):
    spec_version = graphene.Int()

    class Meta:
        model = RuntimeType
