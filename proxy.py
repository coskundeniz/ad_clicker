"""
Gölge kuyusu

gölgeler çıkar kuyudan
karışırlar üçe beşe
adımları dolaşır
takipte izde

ev dediğin kapan
yuvadır korkulara
saklanır
sokaktan sıkılan, bıkan

nice sonra
sokaklara vuran
yıllarla kayıplar

gölgedeki kuyudan çıkar
evdekilerden saklanan

            -- Murathan Mungan
"""

from pathlib import Path

try:
    from selenium.webdriver import ChromeOptions
except ImportError:
    import sys

    packages_path = Path.cwd() / "env" / "Lib" / "site-packages"
    sys.path.insert(0, f"{packages_path}")

    from selenium.webdriver import ChromeOptions


def get_proxies(proxy_file: Path) -> list[str]:
    """Get proxies from file

    :type proxy_file: Path
    :param proxy_file: File containing proxies
    """

    filepath = Path(proxy_file)

    if not filepath.exists():
        raise SystemExit(f"Couldn't find proxy file: {filepath}")

    with open(filepath, encoding="utf-8") as proxyfile:
        proxies = [
            proxy.strip().replace("'", "").replace('"', "")
            for proxy in proxyfile.read().splitlines()
        ]

    return proxies


def install_plugin(
    chrome_options: ChromeOptions, proxy_host: str, proxy_port: int, username: str, password: str
) -> None:
    """Install plugin on the fly for proxy authentication

    :type chrome_options: ChromeOptions
    :param chrome_options: ChromeOptions instance to add plugin
    :type proxy_host: str
    :param proxy_host: Proxy host
    :type proxy_port: int
    :param proxy_port: Proxy port
    :type username: str
    :param username: Proxy username
    :type password: str
    :param password: Proxy password
    """

    manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 3,
    "name": "Chrome Proxy Authentication",
    "background": {
        "service_worker": "background.js"
    },
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "webRequest",
        "webRequestAuthProvider"
    ],
    "host_permissions": [
        "<all_urls>"
    ],
    "minimum_chrome_version": "108"
}
"""

    background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: %s
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
    { urls: ["<all_urls>"] },
    ['blocking']
);
""" % (
        proxy_host,
        proxy_port,
        username,
        password,
    )

    plugin_folder = Path.cwd() / "proxy_auth_plugin"
    plugin_folder.mkdir(exist_ok=True)

    with open(plugin_folder / "manifest.json", "w") as manifest_file:
        manifest_file.write(manifest_json)

    with open(plugin_folder / "background.js", "w") as background_js_file:
        background_js_file.write(background_js)

    chrome_options.add_argument(f"--load-extension={plugin_folder}")
