Pangloss-Zotero
===============

Zotero module for [Pangloss](https://github.com/richardhadden/pangloss-core).

### Features:

- Defines a `ZoteroEntry` node model (based on Pangloss `BaseNode`), which can be used exactly like any other node for data modelling.
- Connects to the Zotero websocket API to watch for changes, and sychronises the database in real time.
- Creates a single `ZoteroConfig` database node, to track the current Zotero library version.

### Installation

- Install the module (from GitHub using Poetry)
```bash
poetry add git+https://github.com/richardhadden/pangloss-zotero.git
````

- Add the module to `Settings.INSTALLED_APPS` in your project's `settings.py`:

```python
class Settings(BaseSettings):
    ...

    INSTALLED_APPS: list[str] = ["pangloss_core", "pangloss_zotero", "your_application"]

    ...
```

- Add Zotero API key and group ID to `Settings.INSTALLED_APPS` in your project's `settings.py`:

```python
class Settings(BaseSettings):
    ...

    INSTALLED_APPS: list[str] = ["pangloss_core", "pangloss_zotero", "your_application"]

    ZOTERO_API_KEY: # Your API key
    ZOTERO_GROUP: # The ID of thte group you wish to track
```

- Use it for something!

```python
from typing import Annotated

from pangloss_core.models import BaseNode, RelationTo, RelationConfig
from pangloss_zotero.models import ZoteroEntry

class DefinitelyFactualStatement(BaseNode):
    statement_content: str
    source: Annotated[
        RelationTo[ZoteroEntry], 
        RelationConfig(reverse_name="is_source_of")]
```

### Status

As with Pangloss, do not use this for anything at all.