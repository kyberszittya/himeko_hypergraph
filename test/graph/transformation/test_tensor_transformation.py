import time
import unittest
import logging


from himeko.common.clock import NullClock
from himeko.hbcm.factories.random.generate_graph import RandomFullHypergraphGenerator
from himeko.hbcm.mapping.tensor_mapping import StarExpansionTransformation
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class TestTensorTransformationStarExpansion(unittest.TestCase):

    def setUp(self):
        self.clock = NullClock()
        self.clock.tick()
        self.generator = RandomFullHypergraphGenerator(self.clock)
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    def test_dense_tensor_transformation_star_expansion(self):
        logger.info("START: test_dense_tensor_transformation_star_expansion")
        #
        root = self.generator.generate(3, 3)
        self.assertIsNotNone(root)
        # Star expansion tensor
        transformation = StarExpansionTransformation()
        # Measure time to encode
        start_time = time.time_ns()
        tensor, n, n_e = transformation.encode(root)
        end_time = time.time_ns()
        dt = (end_time - start_time) / 1e9
        logger.info("Time to encode: {}".format(dt))
        self.assertIsNotNone(tensor)
        self.assertEqual(n, 6)
        self.assertEqual(n_e, 3)
        print(tensor)
        # Ensure aggregated tensor is symmetric
        aggregate_tensor = np.sum(tensor, axis=0)
        self.assertTrue(np.all(aggregate_tensor == aggregate_tensor.T))
        #
        logger.info("END: test_dense_tensor_transformation_star_expansion")

    def test_dense_10_tensor_transformation_star_expansion(self):
        logger.info("START: test_dense_tensor_transformation_star_expansion")
        #
        _n = 10
        _e = 10
        root = self.generator.generate(_n, _e)
        self.assertIsNotNone(root)
        # Star expansion tensor
        transformation = StarExpansionTransformation()
        # Measure time to encode
        start_time = time.time_ns()
        tensor, n, n_e = transformation.encode(root)
        end_time = time.time_ns()
        dt = (end_time - start_time) / 1e9
        logger.info("Time to encode, {} vertices, {} edges: {}".format(_n, _e, dt))
        self.assertIsNotNone(tensor)
        self.assertEqual(n, _n + _e)
        self.assertEqual(n_e, _e)
        # PLT tensor
        #
        logger.info("END: test_dense_tensor_transformation_star_expansion")

    def test_dense_100_tensor_transformation_star_expansion(self):
        logger.info("START: test_dense_tensor_transformation_star_expansion")
        #
        _n = 100
        _e = 100
        root = self.generator.generate(_n, _e)
        self.assertIsNotNone(root)
        # Star expansion tensor
        transformation = StarExpansionTransformation()
        # Measure time to encode
        start_time = time.time_ns()
        tensor, n, n_e = transformation.encode(root)
        end_time = time.time_ns()
        dt = (end_time - start_time) / 1e9
        logger.info("Time to encode, {} vertices, {} edges: {}".format(_n, _e, dt))
        self.assertIsNotNone(tensor)
        self.assertEqual(n, _n + _e)
        self.assertEqual(n_e, _e)
        # PLT tensor
        #
        logger.info("END: test_dense_tensor_transformation_star_expansion")

    def test_dense_100v_10e_tensor_transformation_star_expansion(self):
        logger.info("START: test_dense_tensor_transformation_star_expansion")
        #
        _n = 100
        _e = 10
        root = self.generator.generate(_n, _e)
        self.assertIsNotNone(root)
        # Star expansion tensor
        transformation = StarExpansionTransformation()
        # Measure time to encode
        start_time = time.time_ns()
        tensor, n, n_e = transformation.encode(root)
        end_time = time.time_ns()
        dt = (end_time - start_time) / 1e9
        logger.info("Time to encode, {} vertices, {} edges: {}".format(_n, _e, dt))
        self.assertIsNotNone(tensor)
        self.assertEqual(n, _n + _e)
        self.assertEqual(n_e, _e)
        #
        logger.info("END: test_dense_tensor_transformation_star_expansion")





if __name__ == '__main__':
    unittest.main()