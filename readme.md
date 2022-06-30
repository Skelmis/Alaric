Alaric
---

Providing a beautiful way to interact with MongoDB asynchronously in Python.

---

### Example usage

A simplistic example, read more on the docs!

```python
from motor.motor_asyncio import AsyncIOMotorClient

from alaric import Document

client = AsyncIOMotorClient("Mongo connection url")
database = client["my_database"]
config_document = Document(database, "config")

await config_document.insert({"_id": 1, "data": "hello world"})
...
data = await config_document.find({"_id": 1})
```

---

#### Docs can be found [here](https://alaric.readthedocs.io/)

---

### Support

Want realtime help? Join the discord [here](https://discord.gg/BqPNSH2jPg).

---

### License
This project is licensed under the MIT license

---

### Funding

Want a feature added quickly? Want me to help build your software using Alaric?

Sponsor me [here](https://github.com/sponsors/Skelmis)

---

#### Development

In order to make development easier, I recommend using [motor-stubs](https://github.com/Yian8068/motor-stubs)
if you're planning on doing more than Alaric has to offer. I.e. Using motor itself.
