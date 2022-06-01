import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import *
from alaric.comparison import *
from alaric.logical import *
from alaric.meta import *


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO"])
    db = client["COMPX323"]
    document: Document = Document(db, "movies")

    # 1) {'director': {'$eq': 'Steven Spielberg'}}
    r_1 = await document.find_many(AQ(EQ("director", "Steven Spielberg")))
    print(r_1)

    # 2) {'actor': {'$eq': {'name': 'Mark Hamill'}}}
    r_2 = await document.find_many(AQ(EQ("actor", {"name": "Mark Hamill"})))
    print(r_2)

    # 3) {'$and': [{'director': {'$eq': 'Quentin Tarantino'}}, {'actor': {'$eq': {'name': 'Quentin Tarantino'}}}]}
    r_3 = await document.find_many(
        AQ(
            AND(
                EQ("director", "Quentin Tarantino"),
                EQ("actor", {"name": "Quentin Tarantino"}),
            ),
        )
    )
    print(r_3)

    # 4) {"$query": {}, "$orderby": {"year": 1}}
    r_4 = await document.find_many({"$query": {}, "$orderby": {"year": 1}})
    print(r_4)

    # 5) {'genre': {'$in': ['action', 'fantasy']}}
    r_5 = await document.find_many(AQ(IN("genre", ["action", "fantasy"])))
    print(r_5)

    # 6) {'year': {'$gt': 2005}}
    r_6 = await document.find_many(AQ(GT("year", 2005)))
    print(r_6)

    # 7) {'$and': [{'director': {'$eq': 'Quentin Tarantino'}}, {'$or': [{'actor': {'$eq': {'name': 'Christoph Waltz'}}}, {'actor': {'$eq': {'name': 'Leonardo DiCaprio'}}}]}]}
    r_7 = await document.find_many(
        AQ(
            AND(
                EQ("director", "Quentin Tarantino"),
                OR(
                    EQ("actor", {"name": "Christoph Waltz"}),
                    EQ("actor", {"name": "Leonardo DiCaprio"}),
                ),
            )
        )
    )
    print(r_7)

    # 8) {'director': {'$eq': 'Quentin Tarantino'}}
    r_8 = await document.count(EQ("director", "Quentin Tarantino"))
    print(r_8)

    # 9) {'year': {'$lt': 2000}}
    r_9 = await document.count(LT("year", 2000))
    print(r_9)

    # Un-needed after initial run
    # await document.bulk_insert(
    #     [
    #         {
    #             "title": "Star Wars",
    #             "year": 1977,
    #             "director": "George Lucas",
    #             "genre": "fantasy",
    #             "actor": [
    #                 {"name": "Mark Hamill"},
    #                 {"name": "Carrie Fisher"},
    #                 {"name": "Harrison Ford"},
    #             ],
    #         },
    #         {
    #             "title": "Blade Runner",
    #             "year": 1982,
    #             "director": "Ridley Scott",
    #             "genre": "scifi",
    #             "actor": [{"name": "Harrison Ford"}],
    #         },
    #         {
    #             "title": "The Empire Strikes Back",
    #             "year": 1980,
    #             "director": "Irvin Kershner",
    #             "genre": "fantasy",
    #             "actor": [
    #                 {"name": "Mark Hamill"},
    #                 {"name": "Carrie Fisher"},
    #                 {"name": "Harrison Ford"},
    #             ],
    #         },
    #         {
    #             "title": "Alien",
    #             "year": 1979,
    #             "director": "Ridley Scott",
    #             "genre": "scifi",
    #             "actor": [{"name": "Sigourney Weaver"}],
    #         },
    #         {
    #             "title": "Aliens",
    #             "year": 1986,
    #             "director": "James Cameron",
    #             "genre": "scifi",
    #             "actor": [{"name": "Sigourney Weaver"}],
    #         },
    #         {
    #             "title": "Toy Story",
    #             "year": 1995,
    #             "director": "John Lasseter",
    #             "genre": "fantasy",
    #             "actor": [{"name": "Tom Hanks"}, {"name": "Tim Allen"}],
    #         },
    #         {
    #             "title": "Schindler's List",
    #             "year": 1993,
    #             "director": "Steven Spielberg",
    #             "genre": "drama",
    #             "actor": [{"name": "Liam Neeson"}],
    #         },
    #         {
    #             "title": "E.T.",
    #             "year": 1982,
    #             "director": "Steven Spielberg",
    #             "genre": "fantasy",
    #             "actor": [{"name": "Henry Thomas"}],
    #         },
    #         {
    #             "title": "Raiders of the Lost Ark",
    #             "year": 1981,
    #             "director": "Steven Spielberg",
    #             "genre": "action",
    #             "actor": [{"name": "Harrison Ford"}],
    #         },
    #         {
    #             "title": "Minority Report",
    #             "year": 2002,
    #             "director": "Steven Spielberg",
    #             "genre": "scifi",
    #             "actor": [{"name": "Tom Cruise"}],
    #         },
    #         {
    #             "title": "The Departed",
    #             "year": 2006,
    #             "director": "Martin Scorsese",
    #             "genre": "thriller",
    #             "actor": [
    #                 {"name": "Leonardo Dicaprio"},
    #                 {"name": "Jack Nicholson"},
    #                 {"name": "Matt Damon"},
    #                 {"name": "Mark Wahlberg"},
    #             ],
    #         },
    #         {
    #             "title": "The Prestige",
    #             "year": 2006,
    #             "director": "Christopher Nolan",
    #             "genre": "thriller",
    #             "actor": [
    #                 {"name": "Hugh Jackman"},
    #                 {"name": "Christian Bale"},
    #                 {"name": "Scarlett Johansson"},
    #             ],
    #         },
    #         {
    #             "title": "Reservoir Dogs",
    #             "year": 1992,
    #             "director": "Quentin Tarantino",
    #             "genre": "thriller",
    #             "actor": [
    #                 {"name": "Harvey Keitel"},
    #                 {"name": "Tim Roth"},
    #                 {"name": "Quentin Tarantino"},
    #             ],
    #         },
    #         {
    #             "title": "Inglourious Basterds",
    #             "year": 2009,
    #             "director": "Quentin Tarantino",
    #             "genre": "war",
    #             "actor": [
    #                 {"name": "Brad Pitt"},
    #                 {"name": "Christoph Waltz"},
    #                 {"name": "Melanie Laurent"},
    #             ],
    #         },
    #         {
    #             "title": "Letters from Iwo Jima",
    #             "year": 2006,
    #             "director": "Clint Eastwood",
    #             "genre": "war",
    #             "actor": [{"name": "Ken Watanabe"}],
    #         },
    #         {
    #             "title": "Slumdog Millionaire",
    #             "year": 2008,
    #             "director": "Danny Boyle",
    #             "genre": "drama",
    #             "actor": [{"name": "Dev Patel"}],
    #         },
    #         {
    #             "title": "Django Unchained",
    #             "year": 2012,
    #             "director": "Quentin Tarantino",
    #             "genre": "action",
    #             "actor": [
    #                 {"name": "Jamie Foxx"},
    #                 {"name": "Christoph Waltz"},
    #                 {"name": "Leonardo Dicaprio"},
    #             ],
    #         },
    #         {
    #             "title": "The Dark Knight",
    #             "year": 2008,
    #             "director": "Christopher Nolan",
    #             "genre": "thriller",
    #             "actor": [
    #                 {"name": "Christian Bale"},
    #                 {"name": "Heath Ledger"},
    #                 {"name": "Michael Caine"},
    #             ],
    #         },
    #         {
    #             "title": "Memento",
    #             "year": 2005,
    #             "director": "Christopher Nolan",
    #             "genre": "thriller",
    #             "actor": [{"name": "Guy Pearce"}],
    #         },
    #         {
    #             "title": "127 Hours",
    #             "year": 2010,
    #             "director": "Danny Boyle",
    #             "genre": "drama",
    #             "actor": [{"name": "James Franco"}],
    #         },
    #         {
    #             "title": "Birdman",
    #             "year": 2014,
    #             "director": "Alejandro Gonzalez Innaritu",
    #             "genre": "comedy",
    #             "actor": [{"name": "Michael Keaton"}, {"name": "Edward Norton"}],
    #         },
    #         {
    #             "title": "The Shining",
    #             "year": 1980,
    #             "director": "Stanley Kubrick",
    #             "genre": "horror",
    #             "actor": [{"name": "Jack Nicholson"}],
    #         },
    #         {
    #             "title": "Kill Bill Volume 1",
    #             "year": 2003,
    #             "director": "Quentin Tarantino",
    #             "genre": "action",
    #             "actor": [{"name": "Uma Thurman"}],
    #         },
    #         {
    #             "title": "La La Land",
    #             "year": 2016,
    #             "director": "Damien Chazelle",
    #             "genre": "romance",
    #             "actor": [{"name": "Emma Stone"}, {"name": "Ryan Gosling"}],
    #         },
    #     ]
    # )


if __name__ == "__main__":
    asyncio.run(main())
