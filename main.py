from src.web_app.app import flask_app
from src.web_app.utils import clean_uploads


def main():
    flask_app.run()
    clean_uploads()


if __name__ == "__main__":
    main()
