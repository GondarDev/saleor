from copy import deepcopy

import graphene
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from ...core.permissions import GiftcardPermissions
from ...core.utils.promo_code import generate_promo_code
from ...core.utils.validators import date_passed, user_is_valid
from ...giftcard import events, models
from ...giftcard.error_codes import GiftCardErrorCode
from ...giftcard.notifications import send_gift_card_notification
from ...giftcard.utils import activate_gift_card, deactivate_gift_card
from ..core.descriptions import ADDED_IN_31, DEPRECATED_IN_3X_INPUT
from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ..core.scalars import PositiveDecimal
from ..core.types.common import GiftCardError, PriceInput
from ..core.utils import validate_required_string_field
from ..core.validators import validate_price_precision
from .types import GiftCard, GiftCardEvent


class GiftCardInput(graphene.InputObjectType):
    tag = graphene.String(description=f"{ADDED_IN_31} The gift card tag.")
    expiry_date = graphene.types.datetime.Date(description="The gift card expiry date.")

    # DEPRECATED
    start_date = graphene.types.datetime.Date(
        description=(
            f"Start date of the gift card in ISO 8601 format. {DEPRECATED_IN_3X_INPUT}"
        )
    )
    end_date = graphene.types.datetime.Date(
        description=(
            "End date of the gift card in ISO 8601 format. "
            f"{DEPRECATED_IN_3X_INPUT} Use `expiryDate` from `expirySettings` instead."
        )
    )


class GiftCardCreateInput(GiftCardInput):
    balance = graphene.Field(
        PriceInput, description="Balance of the gift card.", required=True
    )
    user_email = graphene.String(
        required=False,
        description="Email of the customer to whom gift card will be sent.",
    )
    code = graphene.String(
        required=False,
        description=(
            "Code to use the gift card. "
            f"{DEPRECATED_IN_3X_INPUT} The code is now auto generated."
        ),
    )
    note = graphene.String(description="The gift card note from the staff member.")


class GiftCardUpdateInput(GiftCardInput):
    balance_amount = PositiveDecimal(
        description=f"{ADDED_IN_31} The gift card balance amount.", required=False
    )


class GiftCardCreate(ModelMutation):
    class Arguments:
        input = GiftCardCreateInput(
            required=True, description="Fields required to create a gift card."
        )

    class Meta:
        description = "Creates a new gift card."
        model = models.GiftCard
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError
        error_type_field = "gift_card_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)

        # perform only when gift card is created
        if instance.pk is None:
            cleaned_input["code"] = generate_promo_code()
            cls.set_created_by_user(cleaned_input, info)

        cls.clean_expiry_date(cleaned_input, instance)
        cls.clean_balance(cleaned_input, instance)

        if email := data.get("user_email"):
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(
                    {
                        "email": ValidationError(
                            "Provided email is invalid.",
                            code=GiftCardErrorCode.INVALID.value,
                        )
                    }
                )

        return cleaned_input

    @staticmethod
    def set_created_by_user(cleaned_input, info):
        user = info.context.user
        if user_is_valid(user):
            cleaned_input["created_by"] = user
            cleaned_input["created_by_email"] = user.email
        cleaned_input["app"] = info.context.app

    @staticmethod
    def clean_expiry_date(cleaned_input, instance):
        expiry_date = cleaned_input.get("expiry_date")
        if expiry_date and date_passed(expiry_date):
            raise ValidationError(
                {
                    "expiry_date": ValidationError(
                        "Expiry date cannot be in the past.",
                        code=GiftCardErrorCode.INVALID.value,
                    )
                }
            )

    @staticmethod
    def clean_balance(cleaned_input, instance):
        balance = cleaned_input.pop("balance", None)
        if balance:
            amount = balance["amount"]
            currency = balance["currency"]
            try:
                validate_price_precision(amount, currency)
            except ValidationError as error:
                error.code = GiftCardErrorCode.INVALID.value
                raise ValidationError({"balance": error})
            if instance.pk:
                if currency != instance.currency:
                    raise ValidationError(
                        {
                            "balance": ValidationError(
                                "Cannot change gift card currency.",
                                code=GiftCardErrorCode.INVALID.value,
                            )
                        }
                    )
            if not amount > 0:
                raise ValidationError(
                    {
                        "balance": ValidationError(
                            "Balance amount have to be greater than 0.",
                            code=GiftCardErrorCode.INVALID.value,
                        )
                    }
                )
            cleaned_input["currency"] = currency
            cleaned_input["current_balance_amount"] = amount
            cleaned_input["initial_balance_amount"] = amount

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        events.gift_card_issued_event(
            gift_card=instance,
            user=info.context.user,
            app=info.context.app,
        )
        send_gift_card_notification(
            cleaned_input.get("created_by"),
            cleaned_input.get("app"),
            cleaned_input["user_email"],
            instance,
            info.context.plugins,
        )
        events.gift_card_sent(
            gift_card_id=instance.id,
            user_id=info.context.user.id if info.context.user else None,
            app_id=info.context.app.id if info.context.app else None,
            email=cleaned_input["user_email"],
        )


class GiftCardUpdate(GiftCardCreate):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a gift card to update.")
        input = GiftCardUpdateInput(
            required=True, description="Fields required to update a gift card."
        )

    class Meta:
        description = "Update a gift card."
        model = models.GiftCard
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError
        error_type_field = "gift_card_errors"

    @staticmethod
    def clean_balance(cleaned_input, instance):
        amount = cleaned_input.pop("balance_amount", None)

        if amount is None:
            return

        currency = instance.currency
        try:
            validate_price_precision(amount, currency)
        except ValidationError as error:
            error.code = GiftCardErrorCode.INVALID.value
            raise ValidationError({"balance_amount": error})
        cleaned_input["current_balance_amount"] = amount
        cleaned_input["initial_balance_amount"] = amount

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        old_instance = deepcopy(instance)

        data = data.get("input")
        cleaned_input = cls.clean_input(info, instance, data)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)

        if "initial_balance_amount" in cleaned_input:
            events.gift_card_balance_reset(
                instance, old_instance, info.context.user, info.context.app
            )
        if "expiry_date" in cleaned_input:
            events.gift_card_expiry_date_updated(
                instance, old_instance, info.context.user, info.context.app
            )

        return cls.success_response(instance)


class GiftCardDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(description="ID of the gift card to delete.", required=True)

    class Meta:
        description = f"{ADDED_IN_31} Delete gift card."
        model = models.GiftCard
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError
        error_type_field = "gift_card_errors"


class GiftCardDeactivate(BaseMutation):
    gift_card = graphene.Field(GiftCard, description="Deactivated gift card.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of a gift card to deactivate.")

    class Meta:
        description = "Deactivate a gift card."
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError
        error_type_field = "gift_card_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        gift_card_id = data.get("id")
        gift_card = cls.get_node_or_error(
            info, gift_card_id, field="gift_card_id", only_type=GiftCard
        )
        # create event only when is_active value has changed
        create_event = gift_card.is_active
        deactivate_gift_card(gift_card)
        if create_event:
            events.gift_card_deactivated(
                gift_card=gift_card, user=info.context.user, app=info.context.app
            )
        return GiftCardDeactivate(gift_card=gift_card)


class GiftCardActivate(BaseMutation):
    gift_card = graphene.Field(GiftCard, description="Activated gift card.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of a gift card to activate.")

    class Meta:
        description = "Activate a gift card."
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError
        error_type_field = "gift_card_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        gift_card_id = data.get("id")
        gift_card = cls.get_node_or_error(
            info, gift_card_id, field="gift_card_id", only_type=GiftCard
        )
        # create event only when is_active value has changed
        create_event = not gift_card.is_active
        activate_gift_card(gift_card)
        if create_event:
            events.gift_card_activated(
                gift_card=gift_card, user=info.context.user, app=info.context.app
            )
        return GiftCardActivate(gift_card=gift_card)


class GiftCardResendInput(graphene.InputObjectType):
    id = graphene.ID(required=True, description="ID of a gift card to resend.")
    email = graphene.String(
        required=False, description="Email to which gift card should be send."
    )


class GiftCardResend(BaseMutation):
    gift_card = graphene.Field(GiftCard, description="Gift card which has been sent.")

    class Arguments:
        input = GiftCardResendInput(
            required=True, description="Fields required to resend a gift card."
        )

    class Meta:
        description = "Resend a gift card."
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError

    @classmethod
    def clean_input(cls, data):
        if email := data.get("email"):
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(
                    {
                        "email": ValidationError(
                            "Provided email is invalid.",
                            code=GiftCardErrorCode.INVALID.value,
                        )
                    }
                )

    @classmethod
    def get_target_email(cls, data, gift_card):
        return (
            data.get("email") or gift_card.used_by_email or gift_card.created_by_email
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        data = data.get("input")
        cls.clean_input(data)
        gift_card_id = data["id"]
        gift_card = cls.get_node_or_error(
            info, gift_card_id, field="gift_card_id", only_type=GiftCard
        )
        target_email = cls.get_target_email(data, gift_card)
        user = None
        if user_is_valid(info.context.user):
            user = info.context.user
        send_gift_card_notification(
            user,
            info.context.app,
            target_email,
            gift_card,
            info.context.plugins,
        )
        events.gift_card_resent(
            gift_card_id=gift_card.id,
            user_id=user.id if user else None,
            app_id=info.context.app.id if info.context.app else None,
            email=target_email,
        )
        return GiftCardResend(gift_card=gift_card)


class GiftCardAddNoteInput(graphene.InputObjectType):
    message = graphene.String(description="Note message.", required=True)


class GiftCardAddNote(BaseMutation):
    gift_card = graphene.Field(GiftCard, description="Gift card with the note added.")
    event = graphene.Field(GiftCardEvent, description="Gift card note created.")

    class Arguments:
        id = graphene.ID(
            required=True, description="ID of the gift card to add a note for."
        )
        input = GiftCardAddNoteInput(
            required=True,
            description="Fields required to create a note for the gift card.",
        )

    class Meta:
        description = "Adds note to the gift card."
        permissions = (GiftcardPermissions.MANAGE_GIFT_CARD,)
        error_type_class = GiftCardError

    @classmethod
    def clean_input(cls, _info, _instance, data):
        try:
            cleaned_input = validate_required_string_field(data["input"], "message")
        except ValidationError:
            raise ValidationError(
                {
                    "message": ValidationError(
                        "Message can't be empty.",
                        code=GiftCardErrorCode.REQUIRED,
                    )
                }
            )
        return cleaned_input

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        gift_card = cls.get_node_or_error(info, data.get("id"), only_type=GiftCard)
        cleaned_input = cls.clean_input(info, gift_card, data)
        event = events.gift_card_note_added(
            gift_card=gift_card,
            user=info.context.user,
            app=info.context.app,
            message=cleaned_input["message"],
        )
        return GiftCardAddNote(gift_card=gift_card, event=event)
