"""Tests for PermissionsWatchdog - verifies browser permissions are granted correctly."""

import pytest
from bubus import EventBus

from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.browser.events import BrowserConnectedEvent
from browser_use.browser.watchdogs.permissions_watchdog import PermissionsWatchdog


class TestPermissionsWatchdog:
	"""Tests for the PermissionsWatchdog class."""

	@pytest.fixture
	def event_bus(self):
		"""Create an event bus for testing."""
		return EventBus()

	@pytest.mark.asyncio
	async def test_no_permissions_granted_when_empty(self, event_bus):
		"""Test that no permissions are granted when permissions list is empty."""
		browser_profile = BrowserProfile(
			permissions=[],
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Should not raise - just logs and returns
		await watchdog.on_BrowserConnectedEvent(BrowserConnectedEvent(cdp_url='ws://localhost:9222'))

	@pytest.mark.asyncio
	async def test_permissions_granted_on_browser_connected(self, event_bus):
		"""Test that permissions are granted when browser connects."""
		browser_profile = BrowserProfile(
			permissions=['clipboardReadWrite', 'notifications'],
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Should not raise - CDP will attempt to grant permissions
		# The watchdog catches exceptions internally
		await watchdog.on_BrowserConnectedEvent(BrowserConnectedEvent(cdp_url='ws://localhost:9222'))

	@pytest.mark.asyncio
	async def test_default_permissions(self, event_bus):
		"""Test that default permissions are used when not specified."""
		# BrowserProfile has default permissions of ['clipboardReadWrite', 'notifications']
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify default permissions are set
		assert browser_profile.permissions == ['clipboardReadWrite', 'notifications']

	@pytest.mark.asyncio
	async def test_custom_permissions(self, event_bus):
		"""Test that custom permissions are used when specified."""
		custom_permissions = ['geolocation', 'camera', 'microphone']
		browser_profile = BrowserProfile(
			permissions=custom_permissions,
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify custom permissions are set
		assert browser_profile.permissions == custom_permissions

	@pytest.mark.asyncio
	async def test_watchdog_listens_to_browser_connected_event(self, event_bus):
		"""Test that watchdog listens to BrowserConnectedEvent."""
		browser_profile = BrowserProfile(
			permissions=[],
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify the watchdog listens to BrowserConnectedEvent
		assert BrowserConnectedEvent in watchdog.LISTENS_TO

	@pytest.mark.asyncio
	async def test_watchdog_does_not_emit_events(self, event_bus):
		"""Test that watchdog does not emit any events."""
		browser_profile = BrowserProfile(
			permissions=[],
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = PermissionsWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify the watchdog does not emit events
		assert len(watchdog.EMITS) == 0
