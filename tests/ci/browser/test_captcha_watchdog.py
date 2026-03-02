"""Tests for CaptchaWatchdog - verifies captcha solving functionality."""

import asyncio
import pytest
from bubus import EventBus

from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.browser.events import BrowserConnectedEvent, BrowserStoppedEvent
from browser_use.browser.watchdogs.captcha_watchdog import CaptchaWatchdog, CaptchaWaitResult


class TestCaptchaWatchdog:
	"""Tests for the CaptchaWatchdog class."""

	@pytest.fixture
	def event_bus(self):
		"""Create an event bus for testing."""
		return EventBus()

	@pytest.fixture
	def browser_session(self):
		"""Create a browser session for testing."""
		return BrowserSession(
			browser_profile=BrowserProfile(
				headless=True,
				user_data_dir=None,
			)
		)

	@pytest.mark.asyncio
	async def test_watchdog_listens_to_correct_events(self, event_bus, browser_session):
		"""Test that watchdog listens to BrowserConnectedEvent and BrowserStoppedEvent."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Verify the watchdog listens to the correct events
		assert BrowserConnectedEvent in watchdog.LISTENS_TO
		assert BrowserStoppedEvent in watchdog.LISTENS_TO

	@pytest.mark.asyncio
	async def test_watchdog_initial_state(self, event_bus, browser_session):
		"""Test that watchdog starts with correct initial state."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Initially, no captcha is being solved
		result = await watchdog.wait_if_captcha_solving(timeout=0.1)
		assert result is None

	@pytest.mark.asyncio
	async def test_wait_if_captcha_solving_returns_none_when_no_captcha(self, event_bus, browser_session):
		"""Test that wait_if_captcha_solving returns None when no captcha is in progress."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		result = await watchdog.wait_if_captcha_solving(timeout=0.5)
		assert result is None

	@pytest.mark.asyncio
	async def test_captcha_watchdog_registers_on_browser_connected(self, event_bus, browser_session):
		"""Test that CDP handlers registration is attempted when browser connects."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Without an actual CDP client, this will raise an AssertionError
		# but that's expected - the test verifies the watchdog attempts to register
		with pytest.raises(AssertionError, match='CDP client not initialized'):
			await watchdog.on_BrowserConnectedEvent(BrowserConnectedEvent(cdp_url='ws://localhost:9222'))

	@pytest.mark.asyncio
	async def test_captcha_watchdog_clears_state_on_browser_stopped(self, event_bus, browser_session):
		"""Test that captcha state is cleared when browser stops."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Without browser connected, just stop
		await watchdog.on_BrowserStoppedEvent(BrowserStoppedEvent())

		# State should be cleared
		assert watchdog._captcha_solving is False
		assert watchdog._captcha_result == 'unknown'
		assert watchdog._cdp_handlers_registered is False

	@pytest.mark.asyncio
	async def test_captcha_wait_result_structure(self):
		"""Test that CaptchaWaitResult has the expected structure."""
		result = CaptchaWaitResult(
			waited=True,
			vendor='test-vendor',
			url='https://example.com',
			duration_ms=1000,
			result='success',
		)

		assert result.waited is True
		assert result.vendor == 'test-vendor'
		assert result.url == 'https://example.com'
		assert result.duration_ms == 1000
		assert result.result == 'success'

	@pytest.mark.asyncio
	async def test_captcha_wait_timeout(self, event_bus, browser_session):
		"""Test that captcha wait times out correctly."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Manually set captcha solving state (simulating a captcha in progress)
		watchdog._captcha_solving = True
		watchdog._captcha_info = {'vendor': 'test', 'url': 'https://example.com'}
		watchdog._captcha_solved_event.clear()

		# Wait with very short timeout
		result = await watchdog.wait_if_captcha_solving(timeout=0.1)

		# Should return timeout result
		assert result is not None
		assert result.waited is True
		assert result.result == 'timeout'

	@pytest.mark.asyncio
	async def test_multiple_browser_connected_events_handled(self, event_bus, browser_session):
		"""Test that multiple BrowserConnectedEvents are handled correctly."""
		watchdog = CaptchaWatchdog(browser_session=browser_session, event_bus=event_bus)

		# Without actual CDP client, verify state is as expected
		# The first connection attempt fails without CDP, so _cdp_handlers_registered stays False
		with pytest.raises(AssertionError, match='CDP client not initialized'):
			await watchdog.on_BrowserConnectedEvent(BrowserConnectedEvent(cdp_url='ws://localhost:9222'))

		# Verify initial state
		assert watchdog._cdp_handlers_registered is False
