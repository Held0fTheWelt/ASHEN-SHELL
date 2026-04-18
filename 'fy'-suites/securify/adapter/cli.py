from fy_platform.ai.adapter_cli_helper import run_adapter_cli
from securify.adapter.service import SecurifyAdapter


def main(argv=None) -> int:
    return int(run_adapter_cli(SecurifyAdapter, argv))
