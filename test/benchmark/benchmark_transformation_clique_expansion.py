import time
import logging

from himeko.common.clock import NullClock
from himeko.hbcm.factories.random.generate_graph import RandomFullHypergraphGenerator
from himeko.hbcm.mapping.tensor_mapping import BijectiveCliqueExpansionTransformation


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("START: BENCHMARK STAR EXPANSION")

    cnt_nodes = [1, 3, 5, 7, 10, 20, 50, 100, 150, 200, 250]
    cnt_edges = [1, 3, 5, 7, 10, 20, 50, 100, 150, 200, 250]
    transformation = BijectiveCliqueExpansionTransformation()

    clock = NullClock()
    clock.tick()
    generator = RandomFullHypergraphGenerator(clock)

    results = []

    for _n in cnt_nodes:
        for _e in cnt_edges:
            logger.info("n={}, e={}".format(_n, _e))
            root = generator.generate(_n, _e)
            start_time = time.time_ns()
            tensor, n, n_e = transformation.encode(root)
            end_time = time.time_ns()
            dt = (end_time - start_time) / 1e9
            logger.info("Time to encode, {} vertices, {} edges: {}".format(_n, _e, dt))
            del tensor
            results.append((_n, _e, dt))

    # Save results to file
    with open("benchmark_clique_expansion.csv", "w") as f:
        f.write("n,e,dt\n")
        for r in results:
            f.write("{},{},{}\n".format(r[0], r[1], r[2]))


if __name__ == "__main__":
    main()