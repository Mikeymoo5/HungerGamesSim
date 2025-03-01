from pydantic import BaseModel, Field
class Tributes(BaseModel):
    tribute_name: str
    tribute_new_status: str
    tribute_alive: bool

class Time(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)

class Event(BaseModel):
    summary: str
    tributes_involved: list[Tributes]
    time: Time
    
class ResponseSchema(BaseModel):
    day: int
    events: list[Event]