import os
import time
import unittest
import logging

from himeko.common.clock import NullClock
from himeko.hbcm.factories.fixed.basic_hypergraph import SingleFixedHypergraphGenerator7Nodes
from himeko.hbcm.mapping.tensor_mapping import StarExpansionTransformation, BijectiveCliqueExpansionTransformation

import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class TestFixedHypergraphTensor(unittest.TestCase):

    def setUp(self):
        self.clock = NullClock()
        self.clock.tick()
        self.generator = SingleFixedHypergraphGenerator7Nodes(self.clock)
        logger.info("START: setUp")

    def tearDown(self):
        logger.info("END: tearDown")

    def test_fixed_hypergraph_star_expansion_tensor(self):
        logger.info("START: test_fixed_hypergraph_star_expansion_tensor")
        #
        root = self.generator.generate()
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
        self.assertEqual(n, 11)
        self.assertEqual(n_e, 4)
        os.makedirs("output/fixed_hypergraph/star", exist_ok=True)
        # Save images of tensor slices to file
        for i in range(n_e):
            # Save as image
            plt.imshow(tensor[i, :, :], cmap="winter", interpolation="nearest")
            plt.axis('off')
            plt.savefig("output/fixed_hypergraph/star/tensor_{}.png".format(i))
        #
        logger.info("END: test_fixed_hypergraph_star_expansion_tensor")

    def test_fixed_hypergraph_clique_expansion(self):
        logger.info("START: test_fixed_hypergraph_clique_expansion")
        #
        root = self.generator.generate()
        self.assertIsNotNone(root)
        # Star expansion tensor
        transformation = BijectiveCliqueExpansionTransformation()
        # Measure time to encode
        start_time = time.time_ns()
        tensor, n, n_e = transformation.encode(root)
        end_time = time.time_ns()
        dt = (end_time - start_time) / 1e9
        logger.info("Time to encode: {}".format(dt))
        self.assertIsNotNone(tensor)
        self.assertEqual(n, 7)
        self.assertEqual(n_e, 4)
        # Create an output folder for slice images
        os.makedirs("output/fixed_hypergraph/clique", exist_ok=True)
        # Save images of tensor slices to file
        for i in range(n_e):
            # Save as image
            plt.imshow(tensor[i, :, :], cmap="winter", interpolation="nearest")
            plt.axis('off')
            plt.savefig("output/fixed_hypergraph/clique/tensor_{}.png".format(i))
        #
        logger.info("END: test_fixed_hypergraph_clique_expansion")


if __name__ == "__main__":
    unittest.main()
