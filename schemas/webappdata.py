from pydantic import BaseModel


class WebAppData(BaseModel):
    action: int
    order_id: int
    user_id: int
