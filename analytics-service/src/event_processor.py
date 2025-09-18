from abc import ABC, abstractmethod

from pydantic import ValidationError

from shared.logger import get_logger
from shared.models import CartParameters, CategoryParameters, EndSessionParameters, Event, EventParameters, EventType, \
    ProductParameters, \
    PurchaseParameters, StartSessionParameters
from .repository import FirebaseRepository
from .utils import get_event_date

_statistics_collection_name = "statistics"
_sessions_history_collection_name = "sessions_history"
_categories_collection_name = "categories"
_products_collection_name = "products"
_payments_collection_name = "payments"
_countries_collection_name = "countries"
_states_collection_name = "states"
_shipping_collection_name = "shipping"

_lifetime_document_id = "lifetime"
_countries_document_id = "countries"

_started_sessions_field = "started_sessions_count"
_ended_sessions_field = "ended_sessions_count"
_start_time_field = "start_time"
_end_time_field = "end_time"
_user_id_field = "user_id"
_location_field = "location"
_agent_field = "agent"
_views_count_field = "views_count"
_product_related_view_count_field = "product_related_view_count"
_added_to_cart_field = "added_to_cart"
_added_to_cart_quantity_field = "added_to_cart_quantity"
_removed_from_cart_field = "removed_from_cart"
_removed_from_cart_quantity_field = "removed_from_cart_quantity"
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
_total_items_delivered_field = "total_items_delivered"
_items_field = "items"
_total_amount_field = "total_amount"
_discount_amount_field = "discount_amount"
_shipping_address_field = "shipping_address"
_shipping_cost_field = "shipping_cost"
_payment_method_field = "payment_method"
_estimated_delivery_date_field = "estimated_delivery_date"
_shipping_count_field = "shipping_count"
_estimated_delivery_hours_waiting_field = "estimated_delivery_hours_waiting"
_session_duration_seconds_field = "session_duration_seconds"
_total_sessions_duration_seconds_field = "total_sessions_duration_seconds"


def _category_data_collection_path(category_name: str, data_path: str):
    return f"{_categories_collection_name}/{category_name}/{data_path}"


def _product_data_collection_path(product_id: str, data_path: str):
    return f"{_products_collection_name}/{product_id}/{data_path}"


def _payment_data_collection_path(payment_method_id: str, data_path: str):
    return f"{_payments_collection_name}/{payment_method_id}/{data_path}"


def _country_data_collection_path(country: str, data_path: str):
    return f"{_countries_collection_name}/{country}/{data_path}"


def _state_data_collection_path(country: str, state: str, data_path: str):
    return _country_data_collection_path(
        country,
        f"{_states_collection_name}/{state}/{data_path}"
    )


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
        country = event.location.country
        event_date = get_event_date(event)
        country_stats_collection_path = _country_data_collection_path(country, _statistics_collection_name)

        # Set session started info in sessions history
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
        # Increment sessions started count
        for collection in [
            _statistics_collection_name,
            country_stats_collection_path,
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_field(
                    collection_name=collection,
                    document_id=document,
                    field=_started_sessions_field
                )


class CategoryViewedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.CATEGORY_VIEWED, CategoryParameters)

    def _process_body(self, event: Event):
        country = event.location.country
        category_id = event.parameters.category.id
        event_date = get_event_date(event)
        category_stats_collection_path = _category_data_collection_path(category_id, _statistics_collection_name)
        country_category_stats_collection_path = _country_data_collection_path(country, category_stats_collection_path)

        # Add category to session in sessions history
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
        # Increment category views count
        for collection in [
            category_stats_collection_path,
            country_category_stats_collection_path
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_field(
                    collection_name=collection,
                    document_id=document,
                    field=_views_count_field
                )


class ProductViewedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PRODUCT_VIEWED, ProductParameters)

    def _process_body(self, event: Event):
        country = event.location.country
        product_id = event.parameters.product.id
        category_id = event.parameters.product.category.id
        event_date = get_event_date(event)
        product_stats_collection_path = _product_data_collection_path(product_id, _statistics_collection_name)
        country_product_stats_collection_path = _country_data_collection_path(country, product_stats_collection_path)
        category_stats_collection_path = _category_data_collection_path(category_id, _statistics_collection_name)
        country_category_stats_collection_path = _country_data_collection_path(country, category_stats_collection_path)

        # Add product to session in sessions history
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
        # Increment product views count
        for collection in [
            product_stats_collection_path,
            country_product_stats_collection_path,
        ]:
            for document in [
                _lifetime_document_id,
                event_date,
            ]:
                self._repository.increment_field(
                    collection_name=collection,
                    document_id=document,
                    field=_views_count_field
                )
        # Increment category product views count
        for collection in [
            category_stats_collection_path,
            country_category_stats_collection_path,
        ]:
            for document in [
                _lifetime_document_id,
                event_date,
            ]:
                self._repository.increment_field(
                    collection_name=collection,
                    document_id=document,
                    field=_product_related_view_count_field
                )


class ProductCartOperationProcessor(EventProcessor):
    def __init__(
        self,
        repository: FirebaseRepository,
        event_type: EventType,
        cart_operation_field: str,
        cart_operation_quantity_field: str
    ):
        super().__init__(repository, event_type, CartParameters)
        self._cart_operation_field = cart_operation_field
        self.cart_operation_quantity_field = cart_operation_quantity_field

    def _process_body(self, event: Event):
        country = event.location.country
        product_id = event.parameters.product.id
        category_id = event.parameters.product.category.id
        quantity = event.parameters.quantity
        event_date = get_event_date(event)
        product_stats_collection_path = _product_data_collection_path(product_id, _statistics_collection_name)
        country_product_stats_collection_path = _country_data_collection_path(country, product_stats_collection_path)
        category_stats_collection_path = _category_data_collection_path(category_id, _statistics_collection_name)
        country_category_stats_collection_path = _country_data_collection_path(country, category_stats_collection_path)

        # Add/Remove product in cart to session in session history
        self._repository.array_union(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            field=self._cart_operation_field,
            value=[
                {
                    _product_field: product_id,
                    _quantity_field: quantity,
                    _timestamp_field: event.timestamp
                }
            ]
        )
        # Increment product cart count
        for collection in [
            product_stats_collection_path,
            country_product_stats_collection_path,
            category_stats_collection_path,
            country_category_stats_collection_path
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_field(
                    collection_name=collection,
                    document_id=document,
                    field=self.cart_operation_quantity_field,
                    value=quantity
                )


class ProductAddedToCartProcessor(ProductCartOperationProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(
            repository,
            EventType.PRODUCT_ADDED_TO_CART,
            _added_to_cart_field,
            _added_to_cart_quantity_field
        )


class ProductRemovedFromCartProcessor(ProductCartOperationProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(
            repository,
            EventType.PRODUCT_REMOVED_FROM_CART,
            _removed_from_cart_field,
            _removed_from_cart_quantity_field
        )


class PurchaseProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.PURCHASE, PurchaseParameters)

    def _process_body(self, event: Event):
        country = event.location.country
        shipping_country = event.parameters.shipping_address.country
        shipping_state = event.parameters.shipping_address.state
        total_amount = event.parameters.total_amount
        discount_amount = event.parameters.discount_amount
        payment_method_id = event.parameters.payment_method.id
        shipping_cost = event.parameters.shipping_cost
        items_count = sum(item.quantity for item in event.parameters.items)
        total_estimated_delivery_hours_waiting = round(
            (event.parameters.estimated_delivery_date - event.timestamp).total_seconds() / 3600
        )
        event_date = get_event_date(event)
        country_stats_collection_path = _country_data_collection_path(country, _statistics_collection_name)
        payments_stats_collection_path = _payment_data_collection_path(payment_method_id, _statistics_collection_name)
        country_payments_stats_collection_path = _country_data_collection_path(country, payments_stats_collection_path)
        shipping_state_stats_collection_path = _state_data_collection_path(
            shipping_country, shipping_state, _shipping_collection_name)

        # Add purchase to session in sessions history
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
        # Increment purchase info count and amount
        for collection in [
            _statistics_collection_name,
            country_stats_collection_path
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_fields(
                    collection_name=collection,
                    document_id=document,
                    fields=[
                        (_purchase_count_field, 1),
                        (_total_amount_field, total_amount),
                        (_total_discount_field, discount_amount),
                        (_total_items_purchased_field, items_count),
                    ]
                )
        # Increment payment info count and amount
        for collection in [
            payments_stats_collection_path,
            country_payments_stats_collection_path
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_fields(
                    collection_name=collection,
                    document_id=document,
                    fields=[
                        (_usage_count_field, 1),
                        (_total_amount_field, total_amount)
                    ]
                )
        # Increment shipping info count and amount to shipping address state stats
        for document in [
            _lifetime_document_id,
            event_date
        ]:
            self._repository.increment_fields(
                collection_name=shipping_state_stats_collection_path,
                document_id=document,
                fields=[
                    (_shipping_count_field, 1),
                    (_total_items_delivered_field, items_count),
                    (_total_shipping_cost_field, shipping_cost),
                    (_estimated_delivery_hours_waiting_field, total_estimated_delivery_hours_waiting)
                ]
            )
        # Increment product info count and amount for each product in purchase
        for items in event.parameters.items:
            subtotal = items.subtotal
            quantity = items.quantity
            product_id = items.product.id
            category_id = items.product.category.id
            product_stats_collection_path = _product_data_collection_path(product_id, _statistics_collection_name)
            country_product_stats_collection_path = _country_data_collection_path(
                country, product_stats_collection_path)
            category_stats_collection_path = _category_data_collection_path(category_id, _statistics_collection_name)
            country_category_stats_collection_path = _country_data_collection_path(
                country, category_stats_collection_path)

            for collection in [
                product_stats_collection_path,
                country_product_stats_collection_path,
                category_stats_collection_path,
                country_category_stats_collection_path
            ]:
                for document in [
                    _lifetime_document_id,
                    event_date
                ]:
                    self._repository.increment_fields(
                        collection_name=collection,
                        document_id=document,
                        fields=[
                            (_total_amount_field, subtotal),
                            (_total_items_purchased_field, quantity)
                        ]
                    )


class SessionEndedProcessor(EventProcessor):
    def __init__(self, repository: FirebaseRepository):
        super().__init__(repository, EventType.SESSION_ENDED, EndSessionParameters)

    def _process_body(self, event: Event):
        country = event.location.country
        event_date = get_event_date(event)
        country_stats_collection_path = _country_data_collection_path(country, _statistics_collection_name)

        # Set session ended info to session in sessions history
        self._repository.set_document(
            collection_name=_sessions_history_collection_name,
            document_id=event.session_id,
            data={
                _end_time_field: event.timestamp,
                _session_duration_seconds_field: event.parameters.seconds_duration
            }
        )
        # Increment session ended count and total sessions duration
        for collection in [
            _statistics_collection_name,
            country_stats_collection_path
        ]:
            for document in [
                _lifetime_document_id,
                event_date
            ]:
                self._repository.increment_fields(
                    collection_name=collection,
                    document_id=document,
                    fields=[
                        (_ended_sessions_field, 1),
                        (_total_sessions_duration_seconds_field, event.parameters.seconds_duration)
                    ]
                )
