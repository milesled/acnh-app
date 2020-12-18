# The critter classes (Fish & Bug) are designed to hold the pertinent information of each, created using data from 
# the ACNH API and context from the Timezone API. Each class takes two important parameters. The first is a dictionary
# of all the information from the ACNH API. However, the dictionary structure is a bit inconvenient for frequent
# reference, so I decided to store it in an individual object. Furthermore, the class definition requires a hemisphere
# identifier, which is handled by the 'north_or_south' method in the acnh-app file. This allows the system to save only
# the relevant availability information since both northern and southern hemisphere data is provided. Currently, the
# classes both support a __str__() method that returns the name, id number, and availability (months/hours).

class Fish():
    # fish_dict is JSON data passed in, hemi is n_or_s string passed in
    def __init__(self, fish_dict, hemi):
        # basic object identifiers
        self.fish_dict = fish_dict
        self.type = "fish" # used later in image retrieval for URL encoding
        self.id = fish_dict['id'] # id number to use for later reference
        self.name = fish_dict['name']['name-USen'] # english name
        # saving the availability
        self.months = fish_dict['availability']['month-array-'+hemi] # list of months, stored as integers
        self.hours = fish_dict['availability']['time-array'] # list of hours, stored as integers
        # if fish is available year-round, return a custom string, otherwise, return API string
        if fish_dict['availability']['isAllYear'] == True: # variable stored in ACNH API
            self.monthstr = "All Year"
        else:
            self.monthstr = fish_dict['availability']['month-'+hemi] # string of months stored by API
        # same as monthstr, but with the hours of availability instead
        if fish_dict['availability']['isAllDay'] == True: 
            self.timestr = "All Day"
        else:
            self.timestr = fish_dict['availability']['time']

    # the __str__() method here returns the name and id of the fish, followed by the strings of
    # the months and hours for availability. if the fish is either available year-round or all-day,
    # the method will say either "All Year" or "All Day"
    def __str__(self):
        return "==="+self.name+" (%d"%self.id+")"+"===\nmonths: "+self.monthstr+"\ntime: "+self.timestr 

# the Bug class is essentially the same class as Fish, but this time accessing the bug information
# from the ACNH API
class Bug():
    def __init__(self, bug_dict, hemi):
        self.bug_dict = bug_dict 
        self.id = bug_dict['id']
        self.type = "bugs"
        self.name = bug_dict['name']['name-USen']
        self.months = bug_dict['availability']['month-array-'+hemi]
        self.hours = bug_dict['availability']['time-array']
        if bug_dict['availability']['isAllYear'] == True:
            self.monthstr = "All Year"
        else:
            self.monthstr = bug_dict['availability']['month-'+hemi]
        if bug_dict['availability']['isAllDay'] == True:
            self.timestr = "All Day"
        else:
            self.timestr = bug_dict['availability']['time']

    # same as Fish class, but with bugs
    def __str__(self):
        return "==="+self.name+" (%d"%self.id+")"+"===\nmonths: "+self.monthstr+"\ntime: "+self.timestr 