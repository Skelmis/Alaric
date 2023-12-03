from alaric.cached_document import CachedDocument


async def test_get_miss_filling(cached_document: CachedDocument):
    data = {"_id": 1, "value": "value"}
    await cached_document.document.insert(data)

    r_1 = await cached_document._redis_client.get("_id:1|")
    assert r_1 is None

    r_2 = await cached_document.get({"_id": 1})
    assert r_2 == data

    r_3 = await cached_document._redis_client.get("_id:1|")
    assert r_3 is not None


async def test_extra_lookups(cached_document: CachedDocument):
    data = {"_id": 1, "value": "value"}
    await cached_document.document.insert(data)

    r_1 = await cached_document._redis_client.get("value:value|")
    assert r_1 is None

    r_2 = await cached_document.get({"value": "value"})
    assert r_2 == data

    r_3 = await cached_document._redis_client.get("value:value|")
    assert r_3 is not None


async def test_set(cached_document: CachedDocument):
    r_1 = await cached_document._redis_client.get("_id:1|")
    assert r_1 is None

    data = {"_id": 1, "value": "value"}
    await cached_document.set({"_id": 1}, data)

    r_2 = await cached_document._redis_client.get("_id:1|")
    assert r_2 is not None

    r_3 = await cached_document._redis_client.get("value:value|")
    assert r_3 is not None


async def test_duplicate_set(cached_document: CachedDocument):
    r_1 = await cached_document._redis_client.get("_id:1|")
    assert r_1 is None

    data = {"_id": 1, "value": "value"}
    await cached_document.set({"_id": 1}, data)

    r_2 = await cached_document._redis_client.get("_id:1|")
    assert r_2 is not None

    r_3 = await cached_document._redis_client.get("value:value|")
    assert r_3 is not None

    data["value"] = "alaric"
    await cached_document.set({"_id": 1}, data)

    r_2 = await cached_document._redis_client.get("_id:1|")
    assert r_2 is not None

    r_3 = await cached_document._redis_client.get("value:alaric|")
    assert r_3 is not None
