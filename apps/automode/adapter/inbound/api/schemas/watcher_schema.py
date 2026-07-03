from pydantic import BaseModel, Field


class WatcherResponseSchema(BaseModel):
    id: int = Field(0, description="Watcher ID")
    name: str = Field("Watcher", description="Watcher's name")


class WatcherSchema(BaseModel):
    id: int = Field(0, description="Watcher ID")
    name: str = Field("Watcher", description="Watcher's name")
    # 왓처(Watcher Hub) — sherlock_homes 인바운드 게이트웨이, Triage Nurse 역할

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Watcher",
            }
        }
    }
