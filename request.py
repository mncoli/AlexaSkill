import db
import json
from ir import IrishRailRTPI
import string
        
# get time for next train
def train_time():
    train_times = IrishRailRTPI()
    origin = input('origin: ')
    destination = input('destination: ').lower()
    data = json.dumps(train_times.get_station(origin, destination), indent=4, sort_keys=True)
    resp = json.loads(data) #we get a list of dictionaries

    for i in range(len(resp)):
        if resp[i]['destination'].lower()==destination: #filter out by origin and make into lower case for alexa
            if resp[i]['due_in_mins'] == 'Due': #avoid 'next train is due in due minutes' output
                return ('Your train is due now')
            else:
                return ('The next train is in {} mins'.format(resp[i]['due_in_mins']))
            break

def main():
    print(train_time())

if __name__ == '__main__':
    main()

