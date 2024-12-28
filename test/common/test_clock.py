import unittest
from himeko_hypergraph.src.himeko.common.clock import SystemTimeClock, NullClock
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSystemTimeClock(unittest.TestCase):

    def setUp(self):
        self.clock = SystemTimeClock()
        # Logging
        logger.info("START: setUp")

    def tearDown(self):
        # Logging
        logger.info("END: tearDown")

    def test_tick(self):
        logger.info("START: test_tick")
        #
        tick_value = self.clock.tick()
        self.assertIsInstance(tick_value, int)
        #
        logger.info("END: test_tick")

    def test_tick_increases(self):
        logger.info("START: test_tick_increases")
        #
        first_tick = self.clock.tick()
        second_tick = self.clock.tick()
        self.assertGreater(second_tick, first_tick)
        #
        logger.info("END: test_tick_increases")

    def test_nano_sec(self):
        logger.info("START: test_nano_sec")
        #
        tick_value = self.clock.tick()
        self.assertEqual(self.clock.nano_sec, tick_value)
        #
        logger.info("END: test_nano_sec")

    def test_secs(self):
        logger.info("START: test_secs")
        #
        tick_value = self.clock.tick()
        self.assertEqual(self.clock.secs, tick_value / 1e9)
        self.assertEqual(self.clock.secs, self.clock.nano_sec / 1e9)
        # Check if its greater than one
        self.assertGreater(self.clock.secs, 1)
        #
        logger.info("END: test_secs")

    def test_date(self):
        logger.info("START: test_date")
        #
        tick_value = self.clock.tick()
        expected_date = datetime.datetime.fromtimestamp(tick_value / 1e9)
        self.assertEqual(self.clock.date, expected_date)
        #
        logger.info("END: test_date")


class TestNullClock(unittest.TestCase):

    def setUp(self):
        self.clock = NullClock()
        # Logging
        logger.info("START: setUp")

    def tearDown(self):
        # Logging
        logger.info("END: tearDown")

    def test_tick(self):
        logger.info("START: test_tick")
        #
        self.assertEqual(self.clock.tick(), 0)
        #
        logger.info("END: test_tick")

    def test_nano_sec(self):
        logger.info("START: test_nano_sec")
        #
        self.clock.tick()
        self.assertEqual(self.clock.nano_sec, 0)
        #
        logger.info("END: test_nano_sec")

    def test_secs(self):
        logger.info("START: test_secs")
        #
        self.clock.tick()
        self.assertEqual(self.clock.secs, 0)
        #
        logger.info("END: test_secs")

    def test_date(self):
        logger.info("START: test_date")
        #
        self.clock.tick()
        expected_date = datetime.datetime.fromtimestamp(0)
        self.assertEqual(self.clock.date, expected_date)
        #
        logger.info("END: test_date")


if __name__ == '__main__':
    unittest.main()
