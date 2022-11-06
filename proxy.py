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


def install_plugin(chrome_options, proxy_host: str, proxy_port: int, username: str, password: str):
    """Install plugin on the fly for proxy authentication"""

    import zipfile

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"70.0.0"
    }
    """

    background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
    """ % (
        proxy_host,
        proxy_port,
        username,
        password,
    )

    pluginfile = "proxy_auth_plugin.zip"

    with zipfile.ZipFile(pluginfile, "w") as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    chrome_options.add_extension(pluginfile)
