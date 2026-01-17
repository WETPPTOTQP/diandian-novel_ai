import os

from .app import create_app


app = create_app()
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "5000"))
app.run(host=host, port=port, debug=True)

