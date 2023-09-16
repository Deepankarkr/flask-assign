# Flask_Assign

![Alt text](image-3.png)
![Alt text](image-2.png)
![Alt text](image-1.png)


Prior to running

```
from app import app
from app import db

# Create an application context
with app.app_context():
    # Now you can safely use the database
    db.create_all()

```