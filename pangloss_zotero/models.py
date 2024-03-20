from __future__ import annotations

import datetime
import re
import typing
import uuid

from pydantic import HttpUrl

from pangloss_core.models import BaseNode, BaseNodeReference
from pangloss_core.database import Database
from pangloss_core.cypher_utils import cypher
from pangloss_core.exceptions import PanglossConfigError

from pangloss_zotero.zotero_types import ZoteroItemResponse


class ZoteroEntry(BaseNode):
    __create__ = False
    __edit__ = False
    __delete__ = False

    zotero_key: str
    zotero_group_id: int
    zotero_group_name: str
    zotero_version: int
    zotero_url: HttpUrl
    csljson: str
    bib: str
    citation: str

    created_by: str
    created_when: datetime.datetime
    modified_by: str
    modified_when: datetime.datetime

    class Reference(BaseNodeReference):
        citation: str

    def __init_subclass__(cls):
        raise PanglossConfigError("ZoteroEntry cannot be subclassed")

    @staticmethod
    def from_zotero_item_response(item: ZoteroItemResponse):
        label = re.sub("<[^<]+?>", "", (item["citation"]))

        return __class__(
            label=label,
            real_type="ZoteroEntry",
            zotero_key=item["key"],
            zotero_group_id=item["library"]["id"],
            zotero_group_name=item["library"]["name"],
            zotero_version=item["version"],
            zotero_url=item["links"]["self"]["href"],
            csljson=str(item["csljson"]),
            bib=item["bib"],
            citation=item["citation"],
            created_when=item["data"]["dateAdded"],
            created_by=item["meta"]["createdByUser"]["username"],
            modified_when=item["data"]["dateModified"],
            modified_by="",
        )

    async def create_or_update(self):
        (
            node_props,
            params_dict,
        ) = cypher.unpack_properties_to_create_props_and_param_dict(
            self, skip_fields=["uid"], omit_braces=True
        )
        print(node_props)
        key_identifier = cypher.get_unique_string()
        uid_identifier = cypher.get_unique_string()

        cypher_query = f"""
        MERGE (entry:ZoteroEntry {{zotero_key: ${key_identifier}}})
            ON CREATE
        
                SET entry = {{uid: ${uid_identifier}, {node_props}}}
            ON MATCH
                SET entry = {{uid: entry.uid, {node_props}}}
        RETURN entry
        """

        params = {
            uid_identifier: str(self.uid),
            key_identifier: self.zotero_key,
            **params_dict,
        }
        saved_item = await Database.cypher_write(
            cypher_query=cypher_query, params=params
        )
        return saved_item
