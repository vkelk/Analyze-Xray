from app import create_app
from app.config import dev_config


app = create_app(config=dev_config)
# application.run()