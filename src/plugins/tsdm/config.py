from nonebot import get_driver
from pydantic import BaseModel


class Config(BaseModel):
    # Your Config Here
    fastapi_reload: bool = True
    tsdm_base_url: str = "https://www.tsdm39.net"
    tsdm_data_dir: str = 'data'
    tsdm_username: str = ""
    tsdm_password: str = ""
    tsdm_questionid: str = "0"
    tsdm_answer: str = ""

tsdm_config = Config.parse_obj(get_driver().config)