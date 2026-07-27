import os, sys
PROJ = os.path.dirname(os.path.abspath(__file__))

STREAMLIT_PORT = 8501
PWA_PORT = 8080

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="STK">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icons/icon-192.png">
<meta name="theme-color" content="#1a1a2e">
<title>Stock Analysis Tool</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:100%; height:100%; overflow:hidden; background:#0e1117; }
iframe { width:100%; height:100%; border:none; }
</style>
</head>
<body>
<iframe src="http://localhost:STREAMLIT_PORT" allow="camera;microphone;geolocation"></iframe>
<script>
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}
</script>
</body>
</html>"""

HTML = HTML.replace("STREAMLIT_PORT", str(STREAMLIT_PORT))

# Write index.html
with open(os.path.join(PROJ, "pwa", "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
print("index.html written")
