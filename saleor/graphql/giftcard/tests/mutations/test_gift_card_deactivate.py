import graphene

from ....tests.utils import assert_no_permission, get_graphql_content

DEACTIVATE_GIFT_CARD_MUTATION = """
    mutation giftCardDeactivate($id: ID!) {
        giftCardDeactivate(id: $id) {
            errors {
                field
                message
            }
            giftCard {
                isActive
            }
        }
    }
"""


def test_deactivate_gift_card_by_staff(
    staff_api_client, gift_card, permission_manage_gift_card
):
    # given
    assert gift_card.is_active
    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}

    # when
    response = staff_api_client.post_graphql(
        DEACTIVATE_GIFT_CARD_MUTATION,
        variables,
        permissions=[permission_manage_gift_card],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["giftCardDeactivate"]["giftCard"]
    assert data["isActive"] is False


def test_deactivate_gift_card_by_app(
    app_api_client, gift_card, permission_manage_gift_card
):
    # given
    gift_card.is_active = False
    gift_card.save(update_fields=["is_active"])
    assert not gift_card.is_active
    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}

    # when
    response = app_api_client.post_graphql(
        DEACTIVATE_GIFT_CARD_MUTATION,
        variables,
        permissions=[permission_manage_gift_card],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["giftCardDeactivate"]["giftCard"]
    assert data["isActive"] is False


def test_deactivate_gift_card_by_customer(
    api_client,
    gift_card,
):
    # given
    gift_card.is_active = False
    gift_card.save(update_fields=["is_active"])
    assert not gift_card.is_active
    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}

    # when
    response = api_client.post_graphql(
        DEACTIVATE_GIFT_CARD_MUTATION,
        variables,
    )

    # then
    assert_no_permission(response)


def test_deactivate_gift_card_without_premissions(staff_api_client, gift_card):
    # given
    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}

    # when
    response = staff_api_client.post_graphql(DEACTIVATE_GIFT_CARD_MUTATION, variables)

    # then
    assert_no_permission(response)


def test_deactivate_inactive_gift_card(
    staff_api_client, gift_card, permission_manage_gift_card
):
    # given
    gift_card.is_active = False
    gift_card.save(update_fields=["is_active"])
    assert not gift_card.is_active

    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}
    variables = {"id": graphene.Node.to_global_id("GiftCard", gift_card.id)}

    # when
    response = staff_api_client.post_graphql(
        DEACTIVATE_GIFT_CARD_MUTATION,
        variables,
        permissions=[permission_manage_gift_card],
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["giftCardDeactivate"]["giftCard"]
    assert data["isActive"] is False
