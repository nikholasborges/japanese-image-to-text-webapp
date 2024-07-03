from src.web_app.app import flask_app, clean_uploads


def main():
    flask_app.run()
    clean_uploads()


if __name__ == "__main__":
    main()
