import bittensor as bt

from eval_subnet.protocol import (
    GeneratorSynapse,
    DiscriminatorSynapse,
    SolverSynapse,
)
from eval_subnet.validator.reward import (
    score_generator,
    score_discriminator,
    score_solver,
)
from eval_subnet.oracles import lean, docker_grader, chutes, novelty
from eval_subnet.utils.uids import get_random_uids


async def forward(self):
    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    generator_responses = await self.dendrite(
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=GeneratorSynapse(domain="code_python"),
        deserialize=True,
    )
    bt.logging.info(f"Got {len(generator_responses)} generator submissions")

    # TODO phases 2-6: validity gate, discriminator/solver routing, score aggregation
    bt.logging.warning("V8 mechanism: phases 2-6 unimplemented")
