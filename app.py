from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from config import Config
from database import get_db, init_db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    init_db(app)

    @app.route("/")
    def index():
        db = get_db()
        search = request.args.get("search", "").strip()

        if search:
            sql = (
                "SELECT listings.*, users.username "
                "FROM listings "
                "JOIN users ON listings.user_id = users.id "
                "WHERE listings.title LIKE ? "
                "ORDER BY listings.created_at DESC"
            )

            listings = db.execute(
                sql,
                (f"%{search}%",)
            ).fetchall()

        else:
            listings = db.execute(
                """
                SELECT listings.*, users.username
                FROM listings
                JOIN users ON listings.user_id = users.id
                ORDER BY listings.created_at DESC
                """
            ).fetchall()

        return render_template(
            "index.html",
            listings=listings,
            search=search
        )

    @app.route("/listing/<int:listing_id>", methods=["GET", "POST"])
    def listing_detail(listing_id):
        db = get_db()

        listing = db.execute(
            """
            SELECT listings.*, users.username
            FROM listings
            JOIN users ON listings.user_id = users.id
            WHERE listings.id = ?
            """,
            (listing_id,)
        ).fetchone()

        if listing is None:
            return "Объявление не найдено", 404

        if request.method == "POST":
            content = request.form.get("content", "").strip()

            if not content:
                flash("Комментарий не может быть пустым.", "error")
            elif len(content) > 2000:
                flash("Комментарий слишком длинный.", "error")
            else:
                db.execute(
                    """
                    INSERT INTO comments
                    (listing_id, user_id, content)
                    VALUES (?, ?, ?)
                    """,
                    (listing_id, 1, content)
                )

                db.commit()

                flash("Комментарий добавлен.", "success")

            return redirect(
                url_for("listing_detail", listing_id=listing_id)
            )

        comments = db.execute(
            """
            SELECT comments.*, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.listing_id = ?
            ORDER BY comments.created_at ASC
            """,
            (listing_id,)
        ).fetchall()

        return render_template(
            "listing.html",
            listing=listing,
            comments=comments
        )

    @app.route("/create", methods=["GET", "POST"])
    def create_listing():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get(
                "description", ""
            ).strip()

            if not title or not description:
                flash(
                    "Заполните название и описание.",
                    "error"
                )

            elif len(title) > 150 or len(description) > 5000:
                flash(
                    "Название или описание слишком длинное.",
                    "error"
                )

            else:
                db = get_db()

                db.execute(
                    """
                    INSERT INTO listings
                    (user_id, title, description)
                    VALUES (?, ?, ?)
                    """,
                    (1, title, description)
                )

                db.commit()

                flash("Объявление успешно создано.", "success")

                return redirect(url_for("index"))

        return render_template("create_listing.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )