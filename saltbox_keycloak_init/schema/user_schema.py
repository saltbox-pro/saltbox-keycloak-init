import dataclasses


@dataclasses.dataclass
class User:
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
