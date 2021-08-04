from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Generator

from requests import Response

from open_sea_v1.endpoints.endpoint_abc import BaseOpenSeaEndpoint
from open_sea_v1.endpoints.endpoint_client import BaseOpenSeaClient, _ClientParams
from open_sea_v1.endpoints.endpoint_urls import OpenseaApiEndpoints
from open_sea_v1.helpers.extended_classes import ExtendedStrEnum
from open_sea_v1.responses import EventResponse
from open_sea_v1.responses.response_abc import _OpenSeaResponse


class EventType(ExtendedStrEnum):
    """
    The event type to filter. Can be created for new auctions, successful for sales, cancelled, bid_entered, bid_withdrawn, transfer, or approve
    """
    CREATED = 'created'
    SUCCESSFUL = 'successful'
    CANCELLED = 'cancelled'
    BID_ENTERED = 'bid_entered'
    BID_WITHDRAWN = 'bid_withdrawn'
    TRANSFER = 'transfer'
    APPROVE = 'approve'


class AuctionType(ExtendedStrEnum):
    """
    Filter by an auction type. Can be english for English Auctions, dutch for fixed-price and declining-price sell orders (Dutch Auctions), or min-price for CryptoPunks bidding auctions.
    """
    ENGLISH = 'english'
    DUTCH = 'dutch'
    MIN_PRICE = 'min-price'


@dataclass
class _EventsEndpoint(BaseOpenSeaClient, BaseOpenSeaEndpoint):
    """
    Opensea API Events Endpoint

    Parameters
    ----------
    client_params:
        ClientParams instance.

    asset_contract_address:
        The NFT contract address for the assets for which to show events

    event_type:
        The event type to filter. Can be created for new auctions, successful for sales, cancelled, bid_entered, bid_withdrawn, transfer, or approve

    only_opensea:
        Restrict to events on OpenSea auctions. Can be true or false

    auction_type:
        Filter by an auction type. Can be english for English Auctions, dutch for fixed-price and declining-price sell orders (Dutch Auctions), or min-price for CryptoPunks bidding auctions.

    occurred_before:
        Only show events listed before this datetime.

    occurred_after:
        Only show events listed after this datetime.

    api_key:
        Optional Opensea API key, if you have one.

    :return: Parsed JSON
    """
    client_params: _ClientParams = None
    asset_contract_address: str = None
    token_id: Optional[str] = None
    collection_slug: Optional[str] = None
    account_address: Optional[str] = None
    occurred_before: Optional[datetime] = None
    occurred_after: Optional[datetime] = None
    event_type: EventType = None
    auction_type: Optional[AuctionType] = None
    only_opensea: bool = False

    def __post_init__(self):
        self._validate_request_params()

    @property
    def url(self) -> str:
        return OpenseaApiEndpoints.EVENTS.value

    def _get_request(self, **kwargs) -> Response:
        params = dict(
            offset=self.client_params.offset,
            limit=self.client_params.limit,
            asset_contract_address=self.asset_contract_address,
            event_type=self.event_type,
            only_opensea=self.only_opensea,
            collection_slug=self.collection_slug,
            token_id=self.token_id,
            account_address=self.account_address,
            auction_type=self.auction_type,
            occurred_before=self.occurred_before,
            occurred_after=self.occurred_after
        )
        get_request_kwargs = dict(params=params)
        self._http_response = super()._get_request(**get_request_kwargs)
        return self._http_response

    @property
    def parsed_http_response(self) -> list[EventResponse]:
        events_json = self._http_response.json()['asset_events']
        events = [EventResponse(event) for event in events_json]
        return events

    def _validate_request_params(self) -> None:
        self._validate_param_auction_type()
        self._validate_param_event_type()
        self._validate_params_occurred_before_and_occurred_after()

    def _validate_param_event_type(self) -> None:
        if not isinstance(self.event_type, (str, EventType)):
            raise TypeError('Invalid event_type type. Must be str or EventType Enum.', f"{self.event_type=}")

        if self.event_type not in EventType.list():
            raise ValueError('Invalid event_type value. Must be str value from EventType Enum.', f"{self.event_type=}")

    def _validate_param_auction_type(self) -> None:
        if self.auction_type is None:
            return

        if not isinstance(self.auction_type, (str, AuctionType)):
            raise TypeError('Invalid auction_type type. Must be str or AuctionType Enum.', f"{self.auction_type=}")

        if self.auction_type not in AuctionType.list():
            raise ValueError('Invalid auction_type value. Must be str value from AuctionType Enum.',
                             f"{self.auction_type=}")

    def _validate_params_occurred_before_and_occurred_after(self) -> None:
        self._validate_param_occurred_before()
        self._validate_param_occurred_after()
        if self.occurred_after and self.occurred_before:
            self._assert_param_occurred_before_after_cannot_be_same_value()
            self._assert_param_occurred_before_cannot_be_higher_than_occurred_after()

    def _validate_param_occurred_before(self) -> None:
        if not isinstance(self.occurred_before, (type(None), datetime)):
            raise TypeError('Invalid occurred_before type. Must be instance of datetime.',
                            f'{type(self.occurred_before)=}')

    def _validate_param_occurred_after(self) -> None:
        if not isinstance(self.occurred_after, (type(None), datetime)):
            raise TypeError('Invalid occurred_after type. Must be instance of datetime.',
                            f'{type(self.occurred_after)=}')

    def _assert_param_occurred_before_after_cannot_be_same_value(self) -> None:
        if self.occurred_after == self.occurred_before:
            raise ValueError('Params occurred_after and occurred_before may not have the same value.',
                             f"{self.occurred_before=}, {self.occurred_after=}")

    def _assert_param_occurred_before_cannot_be_higher_than_occurred_after(self) -> None:
        if not self.occurred_after < self.occurred_before:
            raise ValueError('Param occurred_before cannot be higher than param occurred_after.',
                             f"{self.occurred_before=}, {self.occurred_after=}")