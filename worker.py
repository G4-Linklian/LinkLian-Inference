import argparse
import asyncio

from app.workers.registry import REGISTRY


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BullMQ Worker runner")
    parser.add_argument(
        "--queue",
        required=True,
        choices=list(REGISTRY.keys()),
        help=f"Name of the queue to run: {list(REGISTRY.keys())}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args   = parse_args()
    klass  = REGISTRY[args.queue]
    worker = klass()
    asyncio.run(worker.run())