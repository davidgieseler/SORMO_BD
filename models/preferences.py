from dataclasses import dataclass


@dataclass
class Preferences:
    fastest: bool = True
    shortest: bool = True
    economical: bool = False
    comfortable: bool = False

    def to_dict(self):
        return {
            "fastest": self.fastest,
            "shortest": self.shortest,
            "economical": self.economical,
            "comfortable": self.comfortable,
        }
