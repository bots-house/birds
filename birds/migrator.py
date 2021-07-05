from typing import Optional
from asyncpg import Pool, Connection
import asyncpg
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import os



class DatabaseNotProvidedError(Exception):
    def __str__(self) -> str:
        return "Database not provided"

DEFAULT_TABLE = "schema_migrations"

class MigrationDirection(str, Enum):
    UP = "up"
    DOWN = "down"


class TransactionMode(str, Enum):
    '''
    Individual - In this mode, each migration is run in it's own isolated transaction.
	If a migration fails, only that migration will be rolled back.

    Signle - In this mode, all migrations are run inside a single transaction. If
	one migration fails, all migrations are rolled back.
    '''
    INDIVIDUAL = "individual"
    SINGLE = "single" 


@dataclass
class Migration:
    id: int
    up: str
    down: str


class Migrator:
    def __init__(
        self,
        dir: str,
        db_url: Optional[str] = None,
        db_pool: Optional[Pool] = None,
        table: Optional[str] = DEFAULT_TABLE,
        transaction_mode: Optional[TransactionMode] = TransactionMode.SINGLE,
    ):
        self.dir = dir
        self.db_url = db_url
        self.db_pool = db_pool
        self.table = table
        self.transaction_mode = transaction_mode


    @staticmethod
    def load_migrations(dir: str) -> list[Migration]:
        filenames = [f for f in os.listdir(dir) if os.path.isfile(f"{dir}/{f}")]
        if not filenames:
            return []

        id_names = [filename.split(".")[0] for filename in filenames]
        id_names = sorted(list(set(id_names)))

        migrations = []
        for id_name in id_names:
            splitted = id_name.split("_")
            id = int(splitted[0])
            up_path = f"{dir}/{id_name}.up.sql"
            down_path = f"{dir}/{id_name}.down.sql"

            with open(up_path, "r") as f:
                up = f.read()
            
            with open(down_path, "r") as f:
                down = f.read()

            migrations.append(
                Migration(
                    id=id,
                    up=up,
                    down=down,
                )
            )

        return migrations

    async def __create_db_pool(self) -> Pool:
        return await asyncpg.create_pool(
            self.db_url,
            min_size=1,
            max_size=1,
        )

    async def exec(self, direction: MigrationDirection, migrations: list[Migration]):

        async with self.db_pool.acquire() as connection:
            await connection.execute(f"create table if not exists {self.table} (version bigint primary key not null, applied_at timestamptz not null)")

            if self.transaction_mode == TransactionMode.SINGLE:

                async with connection.transaction():
                    for migration in migrations:
                        if direction == MigrationDirection.UP:
                            if (await self.is_applied(connection, migration.id)):
                                continue

                            await connection.execute(migration.up)
                            await connection.execute(f"insert into {self.table} (version, applied_at) values($1, $2)", migration.id, datetime.now(timezone.utc))
                        else:
                            if not (await self.is_applied(connection, migration.id)):
                                continue
                            
                            await connection.execute(migration.down)
                            await connection.execute(f"delete from {self.table} where version = $1", migration.id)

            else:
                pass
    
    async def is_applied(self, connection: Connection, migration_id: int) -> bool:
        row = await connection.fetchrow(f"select * from {self.table} where version = $1", migration_id)
        return True if row else False

    async def apply_migrations(self, direction: Optional[MigrationDirection] = MigrationDirection.UP, count: Optional[int] = -1):
        if not self.db_url and not self.db_pool:
            raise DatabaseNotProvidedError
        
        if self.db_url and not self.db_pool:
            self.db_pool = await self.__create_db_pool()

        migrations = self.load_migrations(self.dir)
        if not migrations:
            return

        if direction == MigrationDirection.DOWN:
            migrations.reverse()

        if count != -1:
            migrations = migrations[:count]
        
        await self.exec(direction, migrations=migrations)
