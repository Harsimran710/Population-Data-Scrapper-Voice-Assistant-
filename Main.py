import json
import pyttsx3
import re
import requests
import speech_recognition as SR
import threading
import time

API_Key = "Enter Your API Key Here"
Project_Token = "Enter Your Project Tocken Here"
Run_Token = "Enter Your Run Tocken Here"

class Data:
    def __init__(self,API_Key,Project_Token):
        self.API_Key = API_Key
        self.Project_Token = Project_Token
        self.params = {
            "api_key": self.API_Key
        }
        self.data = self.GetData()

    # Fetch Data From 'HTML' Link -- Used ParseHub
    def GetData(self):
        WebSite = requests.get(f'https://www.parsehub.com/api/v2/projects/{Project_Token}/last_ready_run/data', params={"api_key": API_Key})
        data = json.loads(WebSite.text)
        return data

    # Upddate Data From 'HTML' Link
    def Update_Data(self):
        WebSite = requests.post(f'https://www.parsehub.com/api/v2/projects/{Project_Token}/run', params={"api_key": API_Key})

        def Poll():
            time.sleep(0.5)
            Previous_Data = self.data
            while True:
                New_Data = self.GetData()
                if New_Data != Previous_Data:
                    self.data = New_Data
                    print("Data Updated.")
                    break
                time.sleep(5)


        New_Thread = threading.Thread(target=Poll)
        New_Thread.start()

    # Returns The Current Total Population Of The World 
    def Get_Total_Population(self):
        return self.data['Current_Population']

    # The Following Functions Return The Demographics Of 'Today'
    def Get_Births_Today(self):
        data = self.data['Today']

        for element in data:
            if element['Name'] == 'Births today':
                return element['Data']
    
    def Get_Deaths_Today(self):
        data = self.data['Today']

        for element in data:
            if element['Name'] == 'Deaths today':
                return element['Data']

    def Get_Population_Growth_Today(self):
        data = self.data['Today']

        for element in data:
            if element['Name'] == 'Population Growth today':
                return element['Data']
        
    # The Following Functions Return The Demographics Of 'This Year'
    def Get_Births_ThisYear(self):
        data = self.data['This_Year']

        for element in data:
            if element['Name'] == 'Births this year':
                return element['Data']
    
    def Get_Deaths_ThisYear(self):
        data = self.data['This_Year']

        for element in data:
            if element['Name'] == 'Deaths this year':
                return element['Data']

    def Get_Population_Growth_ThisYear(self):
        data = self.data['This_Year']

        for element in data:
            if element['Name'] == 'Population Growth this year':
                return element['Data']

    def Get_Country_Data(self, Top_20_Countries):
        data = self.data['Top_20_Countries']

        for element in data:
            if element['Name'].lower() ==  Top_20_Countries.lower():
                return element

        return "0"

    def Get_Country_List(self):
        Countries = []
        for element in self.data['Top_20_Countries']:
            Countries.append(element['Name'])

        return Countries

def Speak(text):
    Speech = pyttsx3.init()
    Speech.say(text)
    Speech.runAndWait()

def Get_Audio():
    Aud = SR.Recognizer()
    with SR.Microphone() as source:
        Audio = Aud.listen(source)
        
        # Storing Audio
        Record = ""

        try:
            Record = Aud.recognize_google(Audio)
        except Exception as Exp:
            print("Exception: ", str(Exp))

        return Record

def main():
    print("Program Initiated")
    Popuation = Data(API_Key, Project_Token)
    Quit = "Quit" 
    Update_Command = "Update"
    Country_List = Popuation.Get_Country_List()

    Patterns = {
        re.compile("[\w\s]+ total population [\w\s]+ world"):Popuation.Get_Total_Population,
        re.compile("[\w\s]+ current population [\w\s]+ world"):Popuation.Get_Total_Population,
        re.compile("[\w\s]+ total births [\w\s]+ today"):Popuation.Get_Births_Today,
        re.compile("total births today"):Popuation.Get_Births_Today,
        re.compile("[\w\s]+ total deaths [\w\s]+ today"):Popuation.Get_Deaths_Today,
        re.compile("total deaths today"):Popuation.Get_Deaths_Today,
        re.compile("[\w\s]+ total population growth [\w\s]+ today"):Popuation.Get_Population_Growth_Today,
        re.compile("total population growth today"):Popuation.Get_Population_Growth_Today,
        re.compile("[\w\s]+ total births [\w\s]+ this year"):Popuation.Get_Births_ThisYear,
        re.compile("total births this year"):Popuation.Get_Births_ThisYear,
        re.compile("[\w\s]+ total deaths [\w\s]+ this year"):Popuation.Get_Deaths_ThisYear,
        re.compile("total deaths this"):Popuation.Get_Deaths_ThisYear,
        re.compile("[\w\s]+ total population growth [\w\s]+ this year"):Popuation.Get_Population_Growth_ThisYear,
        re.compile("total population growth this year"):Popuation.Get_Population_Growth_ThisYear
    } 

    Country_Patterns = {
        re.compile("[\w\s]+ population [\w\s]+"): lambda Country: Popuation.Get_Country_Data(Country)['Data']
    }

    # Using The While Loop To Get Audio 
    while True:
        print("Go Ahead...")
        Text = Get_Audio()
        print(Text)
        Ans = None

        for pattern, func in Country_Patterns.items():
            if pattern.match(Text):
                Total_Words = set(Text.split())
                for Country in Country_List:
                    if Country in Total_Words:
                        Ans = func(Country)
                        break

        for pattern, func in Patterns.items():
            if pattern.match(Text):
                Ans = func()
                break
        
        if Ans:
            Speak(Ans)

        # Used To Update The Data
        if Text == Update_Command:
            print("Data is being updated.")
            Popuation.Update_Data()

        # Used To Quit The Program
        if Text.find(Quit) != -1:
            print("Bye!")
            break
        
main()