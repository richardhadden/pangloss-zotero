from pydantic import HttpUrl

from typing import List, Any, TypedDict
from datetime import datetime


Creator = TypedDict("Creator", {"creatorType": str, "firstName": str, "lastName": str})

Data = TypedDict(
    "Data",
    {
        "key": str,
        "version": int,
        "itemType": str,
        "title": str,
        "creators": List[Creator],
        "abstractNote": str,
        "publicationTitle": str,
        "volume": str,
        "issue": str,
        "pages": str,
        "date": str,
        "series": str,
        "seriesTitle": str,
        "seriesText": str,
        "journalAbbreviation": str,
        "language": str,
        "DOI": str,
        "ISSN": str,
        "shortTitle": str,
        "url": str,
        "accessDate": datetime,
        "archive": str,
        "archiveLocation": str,
        "libraryCatalog": str,
        "callNumber": str,
        "rights": str,
        "extra": str,
        "tags": List[Any],
        "collections": List[Any],
        "relations": Any,
        "dateAdded": datetime,
        "dateModified": datetime,
    },
)

IssuedOrAccessed = TypedDict("IssuedOrAccessed", {"date-parts": List[List[int]]})

Author = TypedDict("Author", {"family": str, "given": str})

Attachment = TypedDict(
    "Attachment",
    {"href": str, "type": str, "attachmentType": str, "attachmentSize": int},
)

Links = TypedDict(
    "Links",
    {
        "self": "AlternateOrSelf",
        "alternate": "AlternateOrSelf",
        "attachment": Attachment,
    },
)

Csljson = TypedDict(
    "Csljson",
    {
        "id": str,
        "type": str,
        "title": str,
        "container-title": str,
        "page": str,
        "volume": str,
        "issue": str,
        "URL": str,
        "DOI": str,
        "journalAbbreviation": str,
        "language": str,
        "author": List[Author],
        "issued": IssuedOrAccessed,
        "accessed": IssuedOrAccessed,
    },
)

CreatedByUser = TypedDict(
    "CreatedByUser", {"id": int, "username": str, "name": str, "links": Links}
)

Meta = TypedDict(
    "Meta",
    {
        "createdByUser": CreatedByUser,
        "creatorSummary": str,
        "parsedDate": str,
        "numChildren": int,
    },
)


AlternateOrSelf = TypedDict("AlternateOrSelf", {"href": HttpUrl, "type": str})


Library = TypedDict("Library", {"type": str, "id": int, "name": str, "links": Links})

ZoteroItemResponse = TypedDict(
    "ZoteroItemResponse",
    {
        "key": str,
        "version": int,
        "library": Library,
        "links": Links,
        "meta": Meta,
        "bib": str,
        "citation": str,
        "csljson": Csljson,
        "data": Data,
    },
)
