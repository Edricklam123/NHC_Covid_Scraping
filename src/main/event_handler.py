# Author: Edrick
# Date: 11/25/2022

from enum import Enum

class Prompt_type(Enum):
    SYS = '[SYS]'
    WARNING = '[WARNING]'
    ERROR = '[ERROR]'
    INPUT = '[INPUT]'
    DEBUG = '[DEBUG]'