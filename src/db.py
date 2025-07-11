from motor.motor_asyncio import AsyncIOMotorClient

import config

db_host = config.DB_HOST
db_user = config.DB_USER
db_pass = config.DB_PASS
db_cluster = config.DB_CLUSTER

prefix = "mongodb+srv" if db_cluster else "mongodb"
app_name = f"&appName={db_cluster}" if db_cluster else ""
MONGODB_URI = (
    f"{prefix}://{db_user}:{db_pass}@{db_host}/?retryWrites=true&w=majority{app_name}"
)


class DBHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBHandler, cls).__new__(cls)
        return cls._instance

    async def initialize(self):
        if hasattr(self, "initialized") and self.initialized:
            return

        try:
            self.client = AsyncIOMotorClient(MONGODB_URI)
            self.db_users = self.client["users"]
            self.initialized = True
            print("Successfully connected to MongoDB")
        except errors.ConfigurationError as e:
            print(f"ConfigurationError: {e}")
        except errors.ConnectionFailure as e:
            print(f"ConnectionFailure: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def add_todo(self, user_id, title, description, id):
        collection_name = str(user_id)
        try:
            new_todo = {"title": title, "description": description, "id": id}

            await self.db_users[collection_name].update_one(
                {},
                {"$push": {"todo": new_todo}},
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"Error adding todo item for user {user_id}: {e}")
            return False

    async def remove_todo(self, user_id, id):
        collection_name = str(user_id)
        try:
            result = await self.db_users[collection_name].update_one(
                {}, {"$pull": {"todo": {"id": id}}}
            )

            if result.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error removing todo item for user {user_id}: {e}")
            return False

    async def list_todo(self, user_id):
        collection_name = str(user_id)
        try:
            user_document = await self.db_users[collection_name].find_one({})

            if user_document and "todo" in user_document:
                return user_document["todo"]
            else:
                return []
        except Exception as e:
            print(f"Error getting todo list for user {user_id}: {e}")
            return []

    async def list_all(self):
        try:
            collections = await self.db_users.list_collection_names()

            items = []

            for collection_name in collections:
                collection = self.db_users[collection_name]

                async for user_document in collection.find({}):
                    if "todo" in user_document:
                        todos = user_document["todo"]

                        for todo in todos:
                            items.append(
                                {
                                    "_id": todo.get("id", ""),
                                    "title": todo.get("title", ""),
                                    "description": todo.get("description", ""),
                                    "user": collection_name,
                                }
                            )

            return items

        except Exception as e:
            print(f"Error getting todo lists: {e}")
            return []
