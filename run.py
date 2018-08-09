from app import create_app
from app.config import base_config, dev_config

if __name__ == '__main__':
    app = create_app(dev_config)
    app.run()
