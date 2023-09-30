import asyncio

from faker import Faker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from main import _create_async_engine, Person, Organization

fake = Faker()


def generate_fake_person(identifier: str) -> dict:
    return {
        "name": fake.name(),
        "created_at": fake.date_this_decade(),
        "features": [fake.catch_phrase()[:128] for _ in
                     range(fake.random_int(0, 8))],  # noqa
        "identifier_id": identifier
    }


def generate_fake_organization():
    objects_count = 1_000_000
    # objects_count = 10
    obj_list = []
    while objects_count:
        identifier_id = fake.bothify(text='???-###-???????')
        org = {
            "name": fake.company(),
            "telephone_numbers": [
                fake.basic_phone_number() for _ in
                range(fake.random_int(1, 4))
            ],
            "identifier_id": identifier_id,
            "persons": [
                generate_fake_person(identifier_id) for _ in
                range(fake.random_int(0, 5))
            ]
        }
        obj_list.append(org)
        objects_count -= 1
    return obj_list


async def insert_objects(
    async_session: async_sessionmaker[AsyncSession],
    objects: list
) -> None:
    async with async_session() as session:
        async with session.begin():
            # name
            # telephone_numbers
            # identifier_id
            # persons
            # -----
            # name
            # created_at
            # features
            # identifier_id
            session.add_all(
                instances=[
                    Organization(
                        name=item.get("name"),
                        telephone_numbers=item.get("telephone_numbers"),
                        identifier_id=item.get("identifier_id"),
                        persons=[
                            Person(
                                name=p.get("name"),
                                created_at=p.get("created_at"),
                                features=p.get("features"),
                                identifier_id=p.get("identifier_id")
                            ) for p in item.get("persons")
                        ]
                    ) for item in objects
                ]
            )


async def async_main() -> None:
    async_engine = _create_async_engine()
    async_session = async_sessionmaker(async_engine,
                                       expire_on_commit=False)
    objs = generate_fake_organization()
    await insert_objects(async_session, objs)
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(async_main())
