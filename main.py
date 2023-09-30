import os
from datetime import datetime
from typing import AsyncIterator, Optional, Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings
from sqlalchemy import MetaData, DateTime, func, String, ARRAY, select
from sqlalchemy.ext.asyncio import (async_sessionmaker, create_async_engine,
                                    AsyncSession, AsyncEngine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, \
    relationship, joinedload


class Settings(BaseSettings):
    DB_URL: str = os.environ.get(
        "DB_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432"
    )
    DB_SCHEMA: str = 'custom_schema'
    DB_ECHO: bool = True


settings = Settings.model_validate({})


def _create_async_engine() -> AsyncEngine:
    return create_async_engine(settings.DB_URL, echo=settings.DB_ECHO)


async def get_session() -> AsyncIterator[AsyncSession]:
    async_session = async_sessionmaker(
        bind=_create_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(schema=settings.DB_SCHEMA)

    pk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Person(Base):
    __tablename__ = "persons"
    name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now()
    )
    features: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(128)))
    identifier_id: Mapped[str] = mapped_column(String(16), index=True)


class Organization(Base):
    __tablename__ = "organizations"
    name: Mapped[str] = mapped_column(String(256))
    telephone_numbers: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String(128))
    )
    identifier_id: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        index=True
    )
    persons: Mapped[Optional[list[Person]]] = relationship(
        Person,
        lazy='joined',
        primaryjoin=identifier_id == Person.identifier_id,
        foreign_keys=identifier_id,
        remote_side=Person.identifier_id,
        uselist=True
    )


class PersonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    created_at: datetime
    features: Optional[list[str]]


class ResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    identifier_id: str
    telephone_numbers: Optional[list[str]]
    persons: Optional[list[PersonSchema]] = []


class RequestSchema(BaseModel):
    organization_id: str


class Service:

    @classmethod
    async def get_organization_by_id(
        cls,
        session: AsyncSession,
        organization_id: str
    ) -> dict[Any, Any] | Organization:
        stmt = select(Organization).where(
            Organization.identifier_id == organization_id
        ).options(joinedload(Organization.persons))

        res = await session.execute(stmt)
        result = res.unique().scalar_one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return result


app = FastAPI()


@app.post('/get_organization_by_id', response_model=ResponseModel)
async def get_organization_by_id(
    request_schema: RequestSchema,
    session: AsyncSession = Depends(get_session),
    service: Service = Depends(Service)
):
    return await service.get_organization_by_id(
        session=session,
        organization_id=request_schema.organization_id
    )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        port=5050,
        host="0.0.0.0",
        use_colors=True,
        reload=True
    )
