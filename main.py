import os

from flask import Flask

from src.web.app import web_bp

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "src", "web", "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "src", "web", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.register_blueprint(web_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
