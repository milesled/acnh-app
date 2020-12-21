import io, os, json, urllib, requests
from flask import Flask, request, render_template, url_for, redirect
# my custom written files
from apikey import api_key
from critters import Fish, Bug
from diydisplay import Image

# these are some basic functions to help intialize the flask app
path = os.getcwd()
app = Flask(__name__, template_folder=path+'/templates')
app.secret_key = os.urandom(24)

#################################################################
#                        HELPER METHODS                         #
#################################################################

# time, date, and location request function
# requires an ip address to pass in as a parameter
# returns the 'data' dictionary from the Timezone API request
def timeRequest(ip):
    url = 'https://timezoneapi.io/api/ip/?ip='+ip+'&token='+api_key # stored in a separate file for security
    response = requests.get(url) # this API requires using the 'requests' module
    data = response.json()['data']
    return data

# in this function, we want to make a new time request, and then return
# it as a dictionary of all the important info to display on the clock.
# by writing this as a function, I can refresh the time on my webpage
# when people refresh the page
# also requires an ip address to pass to timeRequest()
def timeUpdate(ip):
    refresh = timeRequest(ip)
    # i feel like most of these variables are pretty self-explanatory
    date_time={
        # time saved as a string in format "hr:min:sec"
        "time": refresh['datetime']['time'],
        "city": refresh['city'],
        "country": refresh['country'],
        "hour": refresh['datetime']['hour_12_wolz'],
        "minute": refresh['datetime']['minutes'],
        "ampm_str": refresh['datetime']['hour_am_pm'].upper(),
        "day": refresh['datetime']['day_full'],
        "day_num": refresh['datetime']['day'],
        "month": refresh['datetime']['month_wilz'],
        "month_str": refresh['datetime']['month_full'],
        "year": refresh['datetime']['year']
    }
    return date_time

# this function detects if the user is in either the Northern or Southern hemisphere depending
# on the latitude recieved from the Timezone API. it strips the string into a float, and then
# determines if the number is positive or negative, and returns the preferred string for the ACNH API
# requires the 'data' dictionary from a timeRequest() instance
def north_or_south(data):
    # location is saved as a string "lat,lng"
    # also coordinates are presented as decimals, so make sure to use float!
    lat = float(data['timezone']['location'].split(',')[0])
    if lat > 0:
       return 'northern'
    elif lat < 0:
        return 'southern'
    # this case shouldn't happen, but written just in case (no pun intended)
    return None

# sometimes in the timeSplit function, the number will be a string
# with an extra zero (i.e. "03") so this function detects if the 
# first character is a zero or not, and returns an integer with
# no leading zeros.
# also comes in handy for safely converting num_str into ints
def removeZero(num_str):
    if num_str[0] == '0':
        return int(num_str[1])
    return int(num_str)

# since the time comes in a single string, I need to split it apart
# and make each of the time into integers. this is important for when
# I'm searching the time lists (integers) for bug and fish availability
def timeSplit(time_str):
    # time is formatted by "hr:min:sec"
    time = time_str.split(':')
    # create a dictionary to store all these variables
    # with the time increment as the key
    times = {
        # make sure that none of the time information has leading zeroes
        'hour': removeZero(time[0]),
        'minute': removeZero(time[1]),
        'second': removeZero(time[2])
    }
    return times

#################################################################
#                          MAIN METHODS                         #
#################################################################

# global variables

# initial request to start the process
HEIGHT = 65 # constant that can be changed here to change in other places in program

# fishLoad() requires the hour & month as integers, and the hemisphere in formatted strings.
# It calls all the fish in one JSON response, then determines if they are currently available based
# on given hour and month. if so, a new Fish object will created, and used to create a respective Image object.
# these two objects will be stored in a nested dictionary, with the key name being the file name.
# at the end, an overall dictionary with the available fish will be returned
def fishLoad(hour, month, n_or_s):
    # requesting without an id at the end will return all fish
    fish_raw = urllib.request.urlopen('http://acnhapi.com/v1/fish/')
    # make it a JSON file
    feesh = json.load(fish_raw) # since technically fish is already plural :/
    feesh_dict = {} # dict of Fish and Image objects to be returned
    # the way the dictionaries are nested, it's important to use keys instead
    # of the main dictionary
    for fish in feesh.keys():
        # this conditional checks if the given fish is available in both the current
        # time and current month. if both conditions are true, then the new object
        # will be initialized and stored in feesh_list. otherwise, the fish will be
        # skipped. this check is used for every fish provided by the ACNH API
        if (hour in feesh[fish]['availability']['time-array'] and
        month in feesh[fish]['availability']['month-array-'+n_or_s]):
            # in critters.py, I have created a Fish class that lets me store
            # the information I want from the API into a local & accessible source.
            fresh_catch = Fish(feesh[fish], n_or_s)
            feesh_dict[fish] = {
                # now using the Fish object, create an Image object with given height
                "img": Image(fresh_catch, HEIGHT),
                "data": fresh_catch # storing the Fish object
            }
    return feesh_dict

# bugLoad() is nearly identical to fishLoad() except with the slight difference
# of calling upon a different URL and creating Bug objects instead of Fish objects.
# see more in-depth documentation in fishLoad()
def bugLoad(hour, month, n_or_s):
    bug_raw = urllib.request.urlopen('http://acnhapi.com/v1/bugs/')
    boog = json.load(bug_raw) # haha silly name
    boog_dict = {} # list of Bug objects to be returned
    for bug in boog.keys():
        if (hour in boog[bug]['availability']['time-array'] and
        month in boog[bug]['availability']['month-array-'+n_or_s]):
            fresh_catch = Bug(boog[bug], n_or_s)
            boog_dict[bug] = {
                "img": Image(fresh_catch, HEIGHT),
                "data": fresh_catch
            }
    return boog_dict  

# compress critter data is a way for me to compile all the relevant fish and bugs,
# then split them into the categories of available now, or available always. I then
# store this information into a set of nested dictionaries which allows me to pass all
# the relevant information to the webpage.
# requires dictionaries for fish and bug data
# reutrns single dictionary of all fish and bug data separated by availability
def compressCritterData(feesh, bugs):
    # storage container
    critter_data = {
        'fish': {'var': {}, 'stat': {}},
        'bugs': {'var': {}, 'stat': {}}
    }
    for fish in feesh:
        # availability check, if available all year and all day
        if feesh[fish]['data'].monthstr == 'All Year' and feesh[fish]['data'].timestr == 'All Day':
            critter_data['fish']['stat'][fish] = feesh[fish]
        else: # otherwise it's a fish that has some kind of variability
            critter_data['fish']['var'][fish] = feesh[fish]
    for bug in bugs: #same thing here as fish, but with bugs
        if bugs[bug]['data'].monthstr == 'All Year' and bugs[bug]['data'].timestr == 'All Day':
            critter_data['bugs']['stat'][bug] = bugs[bug]
        else:
            critter_data['bugs']['var'][bug] = bugs[bug]
    return critter_data # return the single dictionary

# this is the home page, which shows your time, date, general location, and all the bugs
# and fish available to you based off your time and hemispherical location. an important 
# thing to note in this method is that I have to use the Flask request.remote_addr attribute
# since the API provided 'self-detection' pulls the IP address from the server, not the client
@app.route("/", methods=['GET', 'POST'])
def homePage():
    data = timeRequest(request.remote_addr) # get the time data
    n_or_s = north_or_south(data) # use it to determine hemisphere
    date_time = timeUpdate(request.remote_addr) # now compact time/date info into a dictionary
    hour = timeSplit(date_time['time'])['hour'] # pull the hour out to use for fish_load/bug_load.
    month = removeZero(date_time['month']) # same thing with the month
    critter_data = compressCritterData(fishLoad(hour, month, n_or_s), bugLoad(hour, month, n_or_s))
    return render_template('template.html', critter=critter_data, dt=date_time)

# for future miles reference: try to pull the critter object that's already been generated
# to help save processing time with the urllib request

# this page is what the user will see when they click on an individual fish or bug.
# it displays all the selected data and an enlarged version of the critter on the screen.
@app.route("/<critter_type>/<critterID>", methods=['GET','POST'])
def critter_view(critterID, critter_type):
    # make a time request to access time and location data
    data = timeRequest(request.remote_addr)
    n_or_s = north_or_south(data) # hemisphere check
    critter_raw = urllib.request.urlopen('http://acnhapi.com/v1/{}/{}'.format(critter_type, critterID))
    critter = json.load(critter_raw)
    # all the information that I want to display on the webpage
    pass_data = { # this will be the data that fish & bugs both have
        "type": critter_type,
        "name": critter['name']['name-USen'],
        "nameJP": critter['name']['name-JPja'],
        "img": critter['image_uri'],
        "price": critter['price'],
        "catchphrase": critter['catch-phrase'],
        "phrase": critter['museum-phrase']
    }
    
    # the code below is a set of conditionals to set variable keys accordingly 

    # guidance on the differences between fish & bug information
    if critter_type == "fish":
        pass_data["shadow"] = critter['shadow']
        pass_data["pricecj"] = critter['price-cj']
    elif critter_type == "bugs":
        pass_data["priceflick"] = critter['price-flick']
    # outside conditionals for the time and month availabilities
    # if available all day, then show "All Day",
    if critter['availability']['isAllDay']: 
        pass_data["time"] = "All Day"
    else: # else save the times from the server
        pass_data["time"] = critter['availability']['time']
    # if available all year, then show "All Year",
    if critter['availability']['isAllYear']:
        pass_data["months"] = "All Year"
    else: # else save the months from the server
        pass_data["months"] = critter['availability']['month-'+n_or_s]

    # now finally render the data into the template
    return render_template('critter_view.html', data=pass_data)

# the finale, running the app on host '0.0.0.0' for public access, and port 8080
# for the ngnix (i think)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)