"""Tests for ScreenshotWatchdog - verifies screenshot functionality."""

import pytest
from bubus import EventBus

from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.browser.events import ScreenshotEvent
from browser_use.browser.watchdogs.screenshot_watchdog import ScreenshotWatchdog


class TestScreenshotWatchdog:
	"""Tests for the ScreenshotWatchdog class."""

	@pytest.fixture
	def event_bus(self):
		"""Create an event bus for testing."""
		return EventBus()

	@pytest.mark.asyncio
	async def test_watchdog_listens_to_screenshot_event(self, event_bus):
		"""Test that watchdog listens to ScreenshotEvent."""
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = ScreenshotWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify the watchdog listens to ScreenshotEvent
		assert ScreenshotEvent in watchdog.LISTENS_TO

	@pytest.mark.asyncio
	async def test_watchdog_does_not_emit_events(self, event_bus):
		"""Test that watchdog does not emit any events."""
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = ScreenshotWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify the watchdog does not emit events
		assert len(watchdog.EMITS) == 0

	@pytest.mark.asyncio
	async def test_screenshot_event_handler_requires_browser_session(self, event_bus):
		"""Test that ScreenshotEvent handler requires an active browser session."""
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = ScreenshotWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Create a ScreenshotEvent
		event = ScreenshotEvent()

		# Without an active browser session, this should raise an error
		# because get_page_targets() will return empty
		with pytest.raises(Exception):
			await watchdog.on_ScreenshotEvent(event)

	@pytest.mark.asyncio
	async def test_screenshot_with_full_page_option(self, event_bus):
		"""Test ScreenshotEvent with full_page option."""
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = ScreenshotWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Create a full page ScreenshotEvent
		event = ScreenshotEvent(full_page=True)

		# Without active browser, should raise
		with pytest.raises(Exception):
			await watchdog.on_ScreenshotEvent(event)

	@pytest.mark.asyncio
	async def test_screenshot_with_clip_option(self, event_bus):
		"""Test ScreenshotEvent with clip option for partial screenshots."""
		browser_profile = BrowserProfile(
			headless=True,
			user_data_dir=None,
		)
		browser_session = BrowserSession(browser_profile=browser_profile)
		watchdog = ScreenshotWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Create a ScreenshotEvent with clip option
		clip: dict[str, float] = {'x': 0.0, 'y': 0.0, 'width': 100.0, 'height': 100.0}
		event = ScreenshotEvent(clip=clip)

		# Without active browser, should raise
		with pytest.raises(Exception):
			await watchdog.on_ScreenshotEvent(event)
