
class global_info:
    def __init__(self, **keys):

        self.num_factions = 0
        self.factions = []
        self.faction_colors = []
        self.faction_names = []

        self.cities = []
        self.faction_cities = []

        self.people = []
        self.faction_people = []

        # update based on passed parameter
        for k in keys.keys():
            if k in self.__dict__:
                self.__dict__[k] = keys[k]



