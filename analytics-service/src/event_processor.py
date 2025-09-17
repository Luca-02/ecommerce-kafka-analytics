from abc import ABC, abstractmethod

from pydantic import ValidationError

from shared.logger import get_logger
from shared.models import CartParameters, CategoryParameters, EndSessionParameters, Event, EventParameters, EventType, \
    ProductParameters, \
    PurchaseParameters, StartSessionParameters
from .repository import FirebaseRepository
from .utils import get_event_date

_general_stats_collection_name = "general_stats"
_sessions_history_collection_name = "sessions_history"
_categories_collection_name = "categories"
_products_collection_name = "products"
_payments_collection_name = "payments"
_stats_collection_name = "stats"

_lifetime_document_id = "lifetime"
_countries_document_id = "countries"

_started_session_field = "started_sessions_count"
_start_time_field = "start_time"
_user_id_field = "user_id"
_location_field = "location"
_agent_field = "agent"
_view_count_field = "view_count"
_product_related_view_count_field = "product_related_view_count"
_added_to_cart_quantity_field = "added_to_cart_quantity"
_remove_from_cart_quantity_field = "remove_from_cart_quantity"
_purchase_field = "purchase"
_categories_viewed_field = "categories_viewed"
_products_viewed_field = "products_viewed"
_category_field = "category"
_product_field = "product"
_timestamp_field = "timestamp"
_quantity_field = "quantity"
_subtotal_field = "subtotal"
_usage_count_field = "usage_count"
_purchase_count_field = "purchase_count"
_total_discount_field = "total_discount"
_total_shipping_cost_field = "total_shipping_cost"
_total_items_purchased_field = "total_items_purchased"
_items_field = "items"
_total_amount_field = "total_amount"
_discount_amount_field = "discount_amount"
_shipping_address_field = "shipping_address"
_shipping_cost_field = "shipping_cost"
_payment_method_field = "payment_method"
_estimated_delivery_date_field = "estimated_delivery_date"


def _category_stats_collection_path(category_name: str):
    return f"{_categories_collection_name}/{category_name}/{_stats_collection_name}"


def _product_stats_collection_path(product_id: str):
    return f"{_products_collection_name}/{product_id}/{_stats_collection_name}"


def _payments_stats_collection_path(payment_method_id: str):
    return f"{_payments_collection_name}/{payment_method_id}/{_stats_collection_name}"


class EventProcessor(ABC):
    """
    Abstract base class for event handlers.
    """

    def __init__(
        self,
        repository: FirebaseRepository,
        expected_event_type: EventType,
        expected_parameters_model: EventParameters,
    ):
        self._logger = get_logger(component='event-handler')
        self._repository = repository
        self._expected_event_type = expected_event_type
        self._expected_parameters_model = expected_parameters_model

    def _valid_event(self, event: Event) -> bool:
        """
        Validate the event regarding the expected event type and parameters model.

        :param event: Event to validate.
        :return: True if the event is valid, False otherwise.
        """
        if event.event_type != self._expected_event_type:
            self._logger.warning(
                f"Event type mismatch: Expected {self._expected_event_type.value}, but received {event.event_type.value}"
            )
            return False

        try:
            self._expected_parameters_model.model_validate(event.parameters)
            return True
        except ValidationError as e:
            self._logger.error(
                f"Invalid parameters for {event.event_type.value} event: {e}"
            )
            return False

    def process(self, event: Event):
        """
        Validate the event and process it.

        :param event: The event to process.
        """
        # TODO: si potrebbe fare una roba simile per evitare duplicazioni codice
        # if self._valid_event(event):
        #     self._process_default(event)
        #     self._process_country(event)

        if self._valid_event(event):
            self._process_body(event)

    @abstractmethod
    def _process_body(self, event: Event):
        """
        Process the validated event.

        :param event: The validated event to process.
        """
        pass


def get_event_handlers_map(repository: FirebaseRepository) -> dict[EventType, EventProcessor]:
    return {
        EventType.SESSION_STARTED: SessionStartedProcessor(repository),
        EventType.CATEGORY_VIEWED: CategoryViewedProcessor(repository),
        EventType.PRODUCT_VIEWED: ProductViewedProcessor(repository),
        EventType.PRODUCT_ADDED_TO_CART: ProductAddedToCartProcessor(repository),
        EventType.PRODUCT_REMOVED_FROM_CART: ProductRemovedFromCartProcessor(repository),
        EventType.PURCHASE: PurchaseProcessor(repository),
        EventType.SESSION_ENDED: SessionEndedProcessor(repository)
    }


class SessionStartedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.SESSION_STARTED, StartSessionParameters)

    def _process_body(self, event: Event):
        event_date = get_event_date(event)

        # Save lifetime general stats
        self._repository.increment_field(
            collection_name=_general_stats_collection_name,
            document_id=_lifetime_document_id,
            field=_started_session_field
        )
        # Save daily general stats
        self._repository.increment_field(
            collection_name=_general_stats_collection_name,
            document_id=event_date,
            field=_started_session_field
        )
        # Save session info
        self._repository.set_document(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            data={
                _start_time_field: event.timestamp,
                _user_id_field: event.user_id,
                _location_field: event.location.model_dump(),
                _agent_field: event.parameters.user_agent
            }
        )


class CategoryViewedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.CATEGORY_VIEWED, CategoryParameters)

    def _process_body(self, event: Event):
        category_id = event.parameters.category.id
        event_date = get_event_date(event)
        category_stats_collection_path = _category_stats_collection_path(category_id)

        # Save lifetime category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_view_count_field
        )
        # Save daily category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=event_date,
            field=_view_count_field
        )
        # Save session info
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=_categories_viewed_field,
            value=[
                {
                    _category_field: category_id,
                    _timestamp_field: event.timestamp
                }
            ]
        )


class ProductViewedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PRODUCT_VIEWED, ProductParameters)

    def _process_body(self, event: Event):
        product_id = event.parameters.product.id
        category_id = event.parameters.product.category.id
        event_date = get_event_date(event)
        product_stats_collection_path = _product_stats_collection_path(product_id)
        category_stats_collection_path = _category_stats_collection_path(category_id)

        # Save lifetime product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_view_count_field
        )
        # Save daily product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=event_date,
            field=_view_count_field
        )
        # Save lifetime category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_product_related_view_count_field
        )
        # Save daily category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=event_date,
            field=_product_related_view_count_field
        )
        # Save session info
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=_products_viewed_field,
            value=[
                {
                    _product_field: product_id,
                    _timestamp_field: event.timestamp
                }
            ]
        )


class ProductAddedToCartProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PRODUCT_ADDED_TO_CART, CartParameters)

    def _process_body(self, event: Event):
        product_id = event.parameters.product.id
        category_id = event.parameters.product.category.id
        quantity = event.parameters.quantity
        event_date = get_event_date(event)
        product_stats_collection_path = _product_stats_collection_path(product_id)
        category_stats_collection_path = _category_stats_collection_path(category_id)

        # Save lifetime product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_added_to_cart_quantity_field,
            value=quantity
        )
        # Save daily product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=event_date,
            field=_added_to_cart_quantity_field,
            value=quantity
        )
        # Save lifetime category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_added_to_cart_quantity_field,
            value=quantity
        )
        # Save daily category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=event_date,
            field=_added_to_cart_quantity_field,
            value=quantity
        )
        # Save session info
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=_added_to_cart_quantity_field,
            value=[
                {
                    _product_field: product_id,
                    _quantity_field: quantity,
                    _timestamp_field: event.timestamp
                }
            ]
        )


class ProductRemovedFromCartProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PRODUCT_REMOVED_FROM_CART, CartParameters)

    def _process_body(self, event: Event):
        product_id = event.parameters.product.id
        category_id = event.parameters.product.category.id
        quantity = event.parameters.quantity
        event_date = get_event_date(event)
        product_stats_collection_path = _product_stats_collection_path(product_id)
        category_stats_collection_path = _category_stats_collection_path(category_id)

        # Save lifetime product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_remove_from_cart_quantity_field,
            value=quantity
        )
        # Save daily product stats
        self._repository.increment_field(
            collection_name=product_stats_collection_path,
            document_id=event_date,
            field=_remove_from_cart_quantity_field,
            value=quantity
        )
        # Save lifetime category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=_lifetime_document_id,
            field=_remove_from_cart_quantity_field,
            value=quantity
        )
        # Save daily category stats
        self._repository.increment_field(
            collection_name=category_stats_collection_path,
            document_id=event_date,
            field=_remove_from_cart_quantity_field,
            value=quantity
        )
        # Save session info
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=_remove_from_cart_quantity_field,
            value=[
                {
                    _product_field: product_id,
                    _quantity_field: quantity,
                    _timestamp_field: event.timestamp
                }
            ]
        )


class PurchaseProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PURCHASE, PurchaseParameters)

    def _process_body(self, event: Event):
        total_amount = event.parameters.total_amount
        discount_amount = event.parameters.discount_amount
        payment_method_id = event.parameters.payment_method.id
        shipping_cost = event.parameters.shipping_cost
        items_count = sum(item.quantity for item in event.parameters.items)
        event_date = get_event_date(event)
        payments_stats_collection_path = _payments_stats_collection_path(payment_method_id)

        # Save lifetime general stats
        self._repository.increment_fields(
            collection_name=_general_stats_collection_name,
            document_id=_lifetime_document_id,
            fields=[
                (_purchase_count_field, 1),
                (_total_amount_field, total_amount),
                (_total_discount_field, discount_amount),
                (_total_shipping_cost_field, shipping_cost),
                (_total_items_purchased_field, items_count)
            ]
        )
        # Save daily general stats
        self._repository.increment_fields(
            collection_name=_general_stats_collection_name,
            document_id=event_date,
            fields=[
                (_purchase_count_field, 1),
                (_total_amount_field, total_amount),
                (_total_discount_field, discount_amount),
                (_total_shipping_cost_field, shipping_cost),
                (_total_items_purchased_field, items_count)
            ]
        )
        # Save lifetime payment stats
        self._repository.increment_fields(
            collection_name=payments_stats_collection_path,
            document_id=_lifetime_document_id,
            fields=[
                (_usage_count_field, 1),
                (_total_amount_field, total_amount)
            ]
        )
        # Save daily payment stats
        self._repository.increment_fields(
            collection_name=payments_stats_collection_path,
            document_id=event_date,
            fields=[
                (_usage_count_field, 1),
                (_total_amount_field, total_amount)
            ]
        )
        # Save session info
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=_purchase_field,
            value=[
                {
                    _items_field: [
                        {
                            _product_field: items.product.id,
                            _quantity_field: items.quantity,
                            _subtotal_field: items.subtotal,
                        } for items in event.parameters.items
                    ],
                    _total_amount_field: total_amount,
                    _discount_amount_field: discount_amount,
                    _shipping_cost_field: shipping_cost,
                    _payment_method_field: payment_method_id,
                    _shipping_address_field: event.parameters.shipping_address.model_dump(),
                    _estimated_delivery_date_field: event.parameters.estimated_delivery_date,
                    _timestamp_field: event.timestamp,
                }
            ]
        )

        for items in event.parameters.items:
            subtotal = items.subtotal
            quantity = items.quantity
            product_id = items.product.id
            category_id = items.product.category.id
            product_stats_collection_path = _product_stats_collection_path(product_id)
            category_stats_collection_path = _category_stats_collection_path(category_id)

            # Save lifetime product stats
            self._repository.increment_fields(
                collection_name=product_stats_collection_path,
                document_id=_lifetime_document_id,
                fields=[
                    (_total_amount_field, subtotal),
                    (_total_items_purchased_field, quantity)
                ]
            )
            # Save daily product stats
            self._repository.increment_fields(
                collection_name=product_stats_collection_path,
                document_id=event_date,
                fields=[
                    (_total_amount_field, subtotal),
                    (_total_items_purchased_field, quantity)
                ]
            )
            # Save lifetime category stats
            self._repository.increment_fields(
                collection_name=category_stats_collection_path,
                document_id=_lifetime_document_id,
                fields=[
                    (_total_amount_field, subtotal),
                    (_total_items_purchased_field, quantity)
                ]
            )
            # Save daily category stats
            self._repository.increment_fields(
                collection_name=category_stats_collection_path,
                document_id=event_date,
                fields=[
                    (_total_amount_field, subtotal),
                    (_total_items_purchased_field, quantity)
                ]
            )


class SessionEndedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.SESSION_ENDED, EndSessionParameters)

    def _process_body(self, event: Event):
        self._logger.info(f"Session ended: {event}")
