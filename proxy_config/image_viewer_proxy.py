# Adapted from https://github.com/LiberTEM/LiberTEM-jupyter-proxy
import os
import sys
import json
import shutil
import secrets
from tempfile import mkdtemp


def _get_path():
    """
    Gets the path to panel + the app or a wrapper script from config files:

    - {IMAGE_VIEWER_ROOT}/etc/image_viewer_jupyter_proxy.json
    - {sys.prefix}/etc/image_viewer_jupyter_proxy.json

    If no config is found, looks for the image-viewer module
    """
    prefix = os.environ.get("IMAGE_VIEWER_ROOT", sys.prefix)
    config_path = os.path.join(prefix, "etc", "image_viewer_jupyter_proxy.json")
    app_path = None
    panel_path = None

    # first, look up path in config:
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.loads(f.read())
        app_path = config.get('app_path')
        panel_path = config.get('panel_path')

    # if there is no config, or the config doesn't contain the key,
    # check for image_viewer and panel in the current env
    if app_path is None:
        try:
            from image_viewer import APP_FILE
            app_path = APP_FILE
        except (ImportError, ModuleNotFoundError):
            pass
    if panel_path is None:
        panel_path = shutil.which("panel")

    if app_path is None:
        raise FileNotFoundError("Could not find image-viewer in configuration "
                                "or installed in this environment.")

    if panel_path is None:
        raise FileNotFoundError("Could not find panel installation in config "
                                "or installed in this environment.")

    return app_path, panel_path


def make_get_cmd(token):

    def _get_cmd(port):
        token_path = store_token(token)
        app_path, panel_path = _get_path()

        cmd = [
            str(panel_path),
            "serve",
            str(app_path),
            "--allow-websocket-origin=*",
            "--port",
            str(port),
            "--args",
            str(token_path),
        ]

        return cmd
    return _get_cmd


def make_token():
    return secrets.token_urlsafe(32)


def store_token(token):
    """
    Make a temporary directory with access limited to the current user,
    and store the token in a new file in that directory.

    Returns the path to the token file.
    """
    # mkdtemp makes sure the directory is only readable by the current user:
    token_dir = mkdtemp(prefix="image-viewer")
    token_path = os.path.join(token_dir, 'image-viewer-token')
    with open(token_path, 'w') as f:
        f.write(token)
    return token_path


def setup_proxy_config():
    token = make_token()

    return {
        "command": make_get_cmd(token),
        "timeout": 90,
        "request_headers_override": {
            "X-Api-Key": token,
        },
        "new_browser_tab": True,
        "launcher_entry": {
            "enabled": False,
        },
    }
