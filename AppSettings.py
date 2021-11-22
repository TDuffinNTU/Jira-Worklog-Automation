import os
import json

'''
    settings for our app
'''
class AppSettings:
    apikey : str
    email : str
    organisation : str
    testmode : bool

    loaded : bool = False

    dir_path : str = (os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))

    def __init__(self) -> None:
        self.loaded = self.load()

    def load(self) -> bool:
        try:
            with open(self.dir_path) as file:
                data = json.load(file)

                self.apikey = data['apikey']
                self.email = data['email']
                self.organisation = data['organisation']
                self.testmode = data['testmode']
                #print(data['apikey'])
                #print(data['email'])
                #print(data['organisation'])
                #print(data['testmode'])
            return True
        except Exception as e:
            print("ERROR:", e)
            

    def save(self) -> None:
        data = {
            'apikey' : self.apikey,
            'email' : self.email,
            'organisation' : self.organisation,
            'testmode' : self.testmode
        }
        
        with open(self.dir_path, 'w') as file:
            json.dump(data, file)

    def __str__(self) -> str:
        return(f'Settings: \tAPI Key -> {self.apikey}\tEmail -> {self.email}\tOrganisation -> {self.organisation}\tTestMode -> {self.testmode}')
