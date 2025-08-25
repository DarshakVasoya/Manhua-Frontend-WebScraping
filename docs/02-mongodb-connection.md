# MongoDB Connection

- All scripts use `mongodb_connection.py` for authenticated access.
- Edit this file with your credentials if needed.
- Example usage:
```python
from mongodb_connection import get_mongo_client
client = get_mongo_client()
db = client.admin
collection = db["manhwa"]
```
