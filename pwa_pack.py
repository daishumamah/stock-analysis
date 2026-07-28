"""PWA head injection for Streamlit app. Embeds manifest + icons as data URIs."""

import base64, json, os

_PROJ = os.path.dirname(os.path.abspath(__file__))
_ICON_DIR = os.path.join(_PROJ, "pwa", "icons")


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_pwa_head():
    """Returns HTML string to inject into <head> for PWA support."""
    icon_192_b64 = _b64(os.path.join(_ICON_DIR, "icon-192.png"))
    icon_512_b64 = _b64(os.path.join(_ICON_DIR, "icon-512.png"))
    icon_mask_b64 = _b64(os.path.join(_ICON_DIR, "icon-192-maskable.png"))

    manifest = {
        "name": "Stock Analysis Tool",
        "short_name": "STK",
        "description": "Stock and crypto analysis with technical indicators, signal scoring, and risk metrics",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#1a1a2e",
        "theme_color": "#1a1a2e",
        "icons": [
            {"src": f"data:image/png;base64,{icon_192_b64}", "sizes": "192x192", "type": "image/png"},
            {"src": f"data:image/png;base64,{icon_512_b64}", "sizes": "512x512", "type": "image/png"},
            {"src": f"data:image/png;base64,{icon_mask_b64}", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        ],
    }

    manifest_b64 = base64.b64encode(json.dumps(manifest).encode()).decode()

    return f"""<link rel="manifest" href="data:application/json;base64,{manifest_b64}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="STK">
<meta name="theme-color" content="#1a1a2e">
<link rel="apple-touch-icon" href="data:image/png;base64,{icon_192_b64}">
"""
