import logging
import os

from flask_app import ENVIRONMENT

logging.basicConfig(
    format="%(message)s [%(levelname)s]",
    level=10,
    filename=os.path.join("logs", "backend.log"),
)

if ENVIRONMENT != "production":
    # Add a stream handler to the root logger so that the messages are shown in the terminal too.
    logging.getLogger().addHandler(logging.StreamHandler())

log = logging.getLogger()