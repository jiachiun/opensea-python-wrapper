from unittest import TestCase
from datetime import datetime, timedelta

from open_sea_v1.endpoints import EventsEndpoint, EventType, AuctionType


class TestEventsEndpoint(TestCase):
    sample_contract = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"  # punk
    events_default_kwargs = dict(
        offset=0, limit=1, asset_contract_address=sample_contract,
        only_opensea=False, event_type=EventType.SUCCESSFUL,
    )

    @staticmethod
    def create_and_get(**kwargs):
        endpoint = EventsEndpoint(**kwargs)
        endpoint.get_request()
        return endpoint.response

    def test_param_event_type_filters_properly(self):
        updated_kwargs = self.events_default_kwargs | dict(limit=5)
        punks_events = self.create_and_get(**updated_kwargs)
        self.assertTrue(all(e.event_type == EventType.SUCCESSFUL for e in punks_events))

    def test_param_event_type_raises_if_not_from_event_type_enum_values(self):
        updated_kwargs = self.events_default_kwargs | dict(event_type='randomstr')
        self.assertRaises((ValueError, TypeError), self.create_and_get, **updated_kwargs)

    def test_param_auction_type_filters_properly(self):
        updated_kwargs = self.events_default_kwargs | dict(limit=5, auction_type=AuctionType.DUTCH)
        punks_events = self.create_and_get(**updated_kwargs)
        self.assertTrue(all(e.auction_type == AuctionType.DUTCH for e in punks_events))

    def test_param_auction_type_raises_if_not_from_auction_type_enum_values(self):
        updated_kwargs = self.events_default_kwargs | dict(auction_type='randomstr')
        self.assertRaises((ValueError, TypeError), self.create_and_get, **updated_kwargs)

    def test_param_auction_type_raises_if_not_isinstance_of_str(self):
        updated_kwargs = self.events_default_kwargs | dict(auction_type=0.0)
        self.assertRaises((ValueError, TypeError), self.create_and_get, **updated_kwargs)

    def test_param_auction_type_does_not_raise_if_is_none(self):
        updated_kwargs = self.events_default_kwargs | dict(auction_type=None)
        self.create_and_get(**updated_kwargs)

    def test_param_only_opensea_true_filters_properly(self):
        updated_kwargs = self.events_default_kwargs | dict(only_opensea=True, limit=2)
        events = self.create_and_get(**updated_kwargs)
        self.assertTrue(all('opensea.io' in event.asset.permalink for event in events))

    def test_param_only_opensea_false_does_not_filter(self):
        """
        Have no idea how to test this param.
        """
        # updated_kwargs = self.events_default_kwargs | dict(only_opensea=False, offset=1, limit=100)
        # events = self.create_and_get(**updated_kwargs)
        # self.assertTrue(any('opensea.io' not in event.asset.permalink for event in events))
        pass

    def test_param_occurred_before_raises_exception_if_not_datetime_instances(self):
        updated_kwargs = self.events_default_kwargs | dict(occurred_before=True)
        self.assertRaises(TypeError, self.create_and_get, **updated_kwargs)

    def test_param_occurred_before_and_after_raises_exception_if_are_equal_values(self):
        dt_now = datetime.now()
        occurred_params = dict(occurred_before=dt_now, occurred_after=dt_now)
        updated_kwargs = self.events_default_kwargs | occurred_params
        self.assertRaises(ValueError, self.create_and_get, **updated_kwargs)

    def test_param_occurred_before_and_after_does_not_raise_if_both_are_none(self):
        updated_kwargs = self.events_default_kwargs | dict(occurred_before=None, occurred_after=None)
        self.create_and_get(**updated_kwargs)

    def test_param_occurred_after_cannot_be_higher_than_occurred_before(self):
        occurred_before = datetime.now()
        occurred_after = occurred_before + timedelta(microseconds=1)
        occurred_params = dict(occurred_before=occurred_before, occurred_after=occurred_after)
        updated_kwargs = self.events_default_kwargs | occurred_params
        self.assertRaises(ValueError, self.create_and_get, **updated_kwargs)

    def test_param_occurred_after_filters_properly(self):
        occurred_after = datetime(year=2021, month=8, day=1)
        updated_kwargs = self.events_default_kwargs | dict(occurred_after=occurred_after, limit=5)
        events = self.create_and_get(**updated_kwargs)
        transaction_datetimes = [datetime.fromisoformat(event.transaction['timestamp']) for event in events]
        self.assertTrue(all(trans_date >= occurred_after for trans_date in transaction_datetimes))

    def test_param_occurred_before_filters_properly(self):
        occurred_before = datetime(year=2021, month=8, day=1)
        updated_kwargs = self.events_default_kwargs | dict(occurred_before=occurred_before, limit=5)
        events = self.create_and_get(**updated_kwargs)
        transaction_datetimes = [datetime.fromisoformat(event.transaction['timestamp']) for event in events]
        self.assertTrue(all(trans_date < occurred_before for trans_date in transaction_datetimes))

    def test_params_occurred_before_after_work_together(self):
        occurred_after = datetime(year=2021, month=7, day=30)
        occurred_before = datetime(year=2021, month=8, day=2)
        updated_kwargs = self.events_default_kwargs | dict(occurred_after=occurred_after, occurred_before=occurred_before, limit=5)
        events = self.create_and_get(**updated_kwargs)
        transaction_datetimes = [datetime.fromisoformat(event.transaction['timestamp']) for event in events]
        self.assertTrue(all(occurred_after <= trans_date <= occurred_before for trans_date in transaction_datetimes))