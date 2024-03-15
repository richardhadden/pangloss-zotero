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

    ZOTERO_API_KEY: str = # Your API key
    ZOTERO_GROUP: str =  # The ID of thte group you wish to track
```

- By default, the Zotero plugin will not run in development mode (as it's arguably a waste of time). To run it in dev mode, add `ZOTERO_RUN_IN_DEV = True` to to `Settings.INSTALLED_APPS` in your project's `settings.py`:

```python
class Settings(BaseSettings):
    ...

    INSTALLED_APPS: list[str] = ["pangloss_core", "pangloss_zotero", "your_application"]

    ZOTERO_API_KEY: str = # Your API key
    ZOTERO_GROUP: str =  # The ID of thte group you wish to track
    ZOTERO_RUN_IN_DEV: bool = True
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

### Limitations
`ZoteroEntry` **cannot** be subclassed. Zotero entries are controlled entirely by the plugin.

### Notes
- On startup, the plugin will fetch a list of all changes with a version greater than the library version logged in the `ZoteroConfig` node. This means it will download and add the entire library on first run, which could take some time.
    - TODO: There is almost certainly a better way to grab the entire library and add it to the database!
- The Zotero websocket API sometimes fails to authenticate, and just hangs instead. There is a 10 second timeout for the authentication response. The plugin will wait another 10 seconds, then attempt to reconnect. It will ingest all changes that have been missed in the meantime.

### Status

As with Pangloss, do not use this for anything at all.


### Tests

Lacking!