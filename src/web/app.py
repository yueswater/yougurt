import os

from flask import Flask, render_template

from src.bot.app import register_linebot
from src.utils.format_datetime import format_date_only

# Import blueprint
from src.web.views.admin import admin_bp
from src.web.views.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"
    app.jinja_env.filters["format_date_only"] = format_date_only

    # Register admin blueprint
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    register_linebot(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/ping")
    def ping():
        return "pong"

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9487))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
