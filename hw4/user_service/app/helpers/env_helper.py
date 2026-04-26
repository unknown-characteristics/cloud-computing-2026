from dotenv import dotenv_values
import io

def init_env_from_str(data: str, clazz):
    data_dict = dotenv_values(stream=io.StringIO(data))
    return clazz(**data_dict)
