from __future__ import annotations

import os

from app import create_app


app = create_app(os.getenv("FLASK_ENV", "development"))

# if __name__ == "__main__":
#     app.run(
#         host=os.getenv("HOST", "127.0.0.1"),
#         port=int(os.getenv("PORT", "5000")),
#         debug=os.getenv("FLASK_DEBUG", "0") == "1",
#     )

# For the server: 
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
