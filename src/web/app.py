from flask import Flask, render_template

from src.utils.format_datetime import format_date_only

# Import blueprint
from src.web.views.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"
    app.jinja_env.filters["format_date_only"] = format_date_only

    # Register admin blueprint
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
