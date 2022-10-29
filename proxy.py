from pathlib import Path


def get_proxies(proxy_file: Path) -> list[str]:
    """Get proxies from file

    :type proxy_file: Path
    :param proxy_file: File containing proxies
    """

    filepath = Path(proxy_file)

    if not filepath.exists():
        raise SystemExit(f"Couldn't find proxy file: {filepath}")

    with open(filepath) as proxyfile:
        proxies = proxyfile.read().splitlines()

    return proxies
