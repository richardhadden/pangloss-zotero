import asyncio
import json
import logging

import httpx
from rich import print
import websockets

from pangloss_core.background_tasks import background_task
from pangloss_core.database import write_transaction, Transaction

from pangloss_zotero.models import ZoteroEntry
from pangloss_core.settings import SETTINGS

logger = logging.getLogger("uvicorn.info")


ZOTERO_API_KEY: str = SETTINGS.ZOTERO_API_KEY # type: ignore
ZOTERO_GROUP: str = SETTINGS.ZOTERO_GROUP # type: ignore
ZOTERO_RUN_IN_DEV: bool = getattr(SETTINGS, "ZOTERO_RUN_IN_DEV", False)


ZOTERO_WEBSOCKET_AUTH = {
    "action": "createSubscriptions",
    "subscriptions": [
        {
            "apiKey": ZOTERO_API_KEY,
            "topics": [
                f"/groups/{ZOTERO_GROUP}", # type: ignore
            ],
        },
    ],
}





class Zotero:

    @classmethod
    @write_transaction
    async def get_current_database_version(cls, tx: Transaction) -> int:

        query = """
            MERGE (c:ZoteroConfig)
            ON CREATE
                SET c.version = 0
            RETURN c
        """
        try:
            result = await tx.run(query=query, parameters={})
            record = await result.value()
            return dict(record[0])["version"]
        except Exception as e:
            raise (e)

    @classmethod
    @write_transaction
    async def set_current_database_version(cls, tx: Transaction, version: int) -> int:

        query = """
            MERGE (c:ZoteroConfig)
            ON MATCH
                SET c.version = $version
            RETURN c
        """
        try:
            result = await tx.run(query=query, parameters={"version": version})
            record = await result.value()
            return dict(record[0])["version"]
        except Exception as e:
            raise (e)

    @classmethod
    async def fetch_updated_item_and_version_keys(
        cls, version
    ) -> tuple[list[str], int]:

        async with httpx.AsyncClient() as client:

            r = await client.get(
                f"https://api.zotero.org/groups/{ZOTERO_GROUP}/items/?since={version}&format=versions",
                headers={"Authorization": f"Bearer {ZOTERO_API_KEY}"},
            )

            data = r.json()
        new_version = max(data.values()) if data.values() else version
        return list(data.keys()), new_version

    @classmethod
    async def get_item(cls, item_key: str) -> tuple[ZoteroEntry, int]:
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"https://api.zotero.org/groups/2556736/items/{item_key}/?format=json&include=bib,data,citation,csljson",
                    headers={"Authorization": f"Bearer {ZOTERO_API_KEY}"},
                )
            except Exception as e:
                logger.error(f"Getting item {item_key} from Zotero API failed. Status code:", str(e))

          
            data = r.json()
       
            backoff = r.headers.get("backoff", 0)
            with open(f"zotero_items/{item_key}.json", "w") as f:
                f.write(json.dumps(data))

        return ZoteroEntry.from_zotero_item_response(data), backoff

    @classmethod
    async def synchronise_to_current(cls):
      
        current_version = await Zotero.get_current_database_version()
    

        try:
            updated_keys, latest_version = await Zotero.fetch_updated_item_and_version_keys(
                current_version
            )
        except Exception:
            logger.error("Error getting updated Zotero entry keys")
        
      

        logger.info(
            f"Fetched Zotero updated keys up to version {latest_version} ({len(updated_keys)} items)"
        )
        try:
            for i, key in enumerate(updated_keys):
                logger.info(f"Fetching Zotero item {i}:", key)
                try:
                    zotero_item, backoff_time = await Zotero.get_item(key)
                except Exception:
                    logger.error("Error getting Zotero Item")
          
                try:
                    await zotero_item.create_or_update()
                    logger.info(f"Writing Zotero item {i}:", key)
                except Exception:
                    logger.error("Error writing Zotero item to database")
                

        except Exception:
            logger.error("Zotero synchronisation error")

        await Zotero.set_current_database_version(latest_version)





@background_task(run_in_dev=ZOTERO_RUN_IN_DEV)
async def zotero_listener():
    logger.info("Starting Zotero connection")
    await Zotero.synchronise_to_current()
    
    uri = "wss://stream.zotero.org"

    async with websockets.connect(uri, logger=logger) as websocket:
        logger.info("Starting Zotero websocket connection.")
        connection_response = await websocket.recv()
        try:
            connection_data = json.loads(connection_response)
            assert connection_data["event"] == "connected"
        except json.JSONDecodeError:
            logger.error("Zotero websocket listener failed to connect")
        except AssertionError:
            logger.error("Zotero websocket listener failed to connect")
        except Exception as e:
            logger.error("Error with Zotero websocket connection:", e)

        try:
            logger.info("Starting Zotero websocket authentication.")
            await websocket.send(json.dumps(ZOTERO_WEBSOCKET_AUTH))
        except Exception as e:
            logger.error("Error with Zotero websocket authentication:", e)
        
        try:
            # Getting an authentication repsonse sometimes hangs;
            # Wrap this in a timeout, which throws error after ten seconds
            # and re-calls this function
            logger.info("Waiting for Zotero Authentication response.")
            async with asyncio.timeout(10):
                subscription_response = await websocket.recv()
        except Exception as e:
            logger.error("Error awaiting Zotero websocket authentication response. Retrying in 10 seconds.")
            await websocket.close()
            await asyncio.sleep(10)
            return (await zotero_listener())

        try:
            subscription_data = json.loads(subscription_response)
            assert subscription_data["event"] == "subscriptionsCreated"
            assert (
                subscription_data["subscriptions"] == ZOTERO_WEBSOCKET_AUTH["subscriptions"]
            )
            assert not subscription_data["errors"]

        except json.JSONDecodeError:
            logger.error("Zotero websocket listener failed to connect")
        except AssertionError:
            logger.error("Zotero websocket listener failed to connect")
        except Exception as e:
            logger.error(e)
        
            
        logger.info(f"Zotero websocket listener connected and authorised. Following changes of {str(ZOTERO_WEBSOCKET_AUTH['subscriptions'][0]["topics"])}")

        while True:
            update_response = await websocket.recv()
            update_data = json.loads(update_response)
            logger.info("Update to Zotero library received")
            if update_data["event"] == "topicUpdated":
                await Zotero.synchronise_to_current()



