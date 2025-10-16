from dataclasses import dataclass
from datetime import datetime

@dataclass
class Adotante:
   id_adotante: int
   rendamedia: int
   temfilhos: int
   estado_saude: str