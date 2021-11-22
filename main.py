import dataclasses
import datetime
from PySimpleGUI.PySimpleGUI import Window
import requests
import json
import base64

import PySimpleGUI  as sg

from Issues import *
from AppSettings import *


'''
    class for some fancy colours :)
    https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

''' 
    Testing authentication
'''
def TestAuth(issues : list[IssueInfo], authToken : str):
    headers = {
            'authorization':f'Basic {authToken}',
            'content-type':'application/json',
            'accept':'application/json'        
        }

    #print("TESTING AUTH")
    count200 = 0
    
    for issue in issues:
        url = f'https://dyedurham.atlassian.net/rest/api/3/issue/{issue.code}/worklog'                   

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            count200 += 1
            
        #print (f'Status: {f"{bcolors.OKBLUE}Success" if response.status_code == 200 else f"{bcolors.FAIL}Failed"}    IssueCode: {issue.code} \t Message[0:64]: [ {response.text[0:64]} ...]{bcolors.ENDC}')

    messagebox("TESTING COMPLETE",f"{(count200 / len(issues)) * 100}% PASSED")


'''
    sends off our timesheets
'''
def Run(month : int, days : list[int], issues : list[IssueInfo], authToken : str): 
    successCount : int = 0
    failedSends : str = ''

    headers = {
                'authorization':f'Basic {authToken}',
                'content-type':'application/json',
                'accept':'application/json'        
            }
    
    for day in days:        
        for issue in issues:
            url = f'https://dyedurham.atlassian.net/rest/api/3/issue/{issue.code}/worklog'             
               
            payload = {
                'timeSpentSeconds':int(issue.duration * 3600),
                'comment': {
                    'type':'doc',
                    'version':1,
                    'content': [{
                        'type':'paragraph',
                        'content':[{
                            'text':f'{issue.comment}',
                            'type':'text'
                        }]                
                    }]
                    },
                'started':f'2021-{month}-{day}T{issue.startHr}:{issue.startMin}:00.000+0000'
            }           
                          
            response = requests.post(url, headers=headers, data=json.dumps(payload)) 

            if response.status_code == 201:
                successCount += 1
            else:
                failedSends += f'\n{issue.code}: {issue.comment} // ERROR: {response.text[0:32]}'

    messagebox('Submission info', f'Success count: {successCount}\nFailures:\n{failedSends}')
            #print(f'Status: {f"{bcolors.OKBLUE}Sent" if response.status_code == 201 else f"{bcolors.FAIL}ERROR: {response.status_code} -> {response.text[0:32]}"} \t Date: {day}/{month}/21 \t Issue:{issue} \t Comment:{issue.comment}{bcolors.ENDC}\n') 

'''
    sort the list of issues by time started
'''
def sortIssuesByStartTime(vals : list[IssueInfo]) -> list[IssueInfo]:
    return sorted(vals, key = lambda x: x.startHr + (x.startMin / 60), reverse=False)

'''
    launch and handle events from settings page
'''
def settingsPage(settings : AppSettings) -> None:
    settingsLayout = [
        [
            [sg.Text('Jira API Key')],
            [sg.Input(settings.apikey if settings.loaded else '', size=(30,1), key='-apikey-',password_char='*')],
            [sg.Text('User Email')],
            [sg.Input(settings.email if settings.loaded else '', size=(30,1), key='-email-')],
            [sg.Text('Organisation Name')],
            [sg.Input(settings.organisation if settings.loaded else '', size=(30,1), key='-org-')],            
            [sg.Checkbox('Testmode', default = settings.testmode if settings.loaded else False, key='-testmode-')],
            [sg.Button('SAVE SETTINGS'), sg.Button('CANCEL', button_color=('white', 'red'))]
        ]
    ]

    window = sg.Window('App Settings', settingsLayout)
    while True:
        event, values = window.read()
        if event == "CANCEL" or event == sg.WIN_CLOSED:
            break
        if event == "SAVE SETTINGS":
            settings.apikey = values['-apikey-']
            settings.email = values['-email-']
            settings.organisation = values['-org-']
            settings.testmode = values['-testmode-']
            settings.save()
            break
    window.close()

'''
    messagebox implementation
'''
def messagebox(title:str, message:str):
    layout = [
        [
            [sg.Multiline(message, size=(40,10), disabled=True)],
            [sg.Button('CLOSE')]
        ]
    ]

    window = sg.Window(title, layout).read()


'''
    main function runs while keeping variables to a safe scope
'''
def main() -> None:
    settings = AppSettings()
    #print(settings.loaded)
    if not settings.loaded:
        settingsPage(settings)
    
    #print (settings)

    lVals : list[IssueInfo] = []
    selectedIssue = None

    leftCol = [
        [sg.Text('Submit Timesheet FROM', size=(25,1), key='-startDay-', enable_events=True), sg.CalendarButton('START', size=(10, 1))], 
        [sg.Text('Submit Timesheet TO', size=(25,1), key='-endDay-', enable_events=True), sg.CalendarButton('END', size=(10, 1))],
        [sg.HSep()],
        [sg.Text('Issues')],
        [sg.Listbox(values=lVals, size=(64,20), enable_events=True, k='-lb-')],
        [sg.Button('NEW ISSUE'), sg.Button('DEL ISSUE')]
    ]

    rightCol = [
        [sg.Button('SETTINGS')],
        [sg.Text('Code')],
        [sg.Input('', size=(15,1), enable_events=True, key='-code-')],
        [sg.Text('Comment')],
        [sg.Input('', size=(15,2), enable_events=True, key='-comment-')],
        [sg.Text('Started')],
        [sg.Text('hr'), sg.Input('', size=(3,1), enable_events=True, key='-hrstart-'), sg.Text('min'), sg.Input('', size=(3,1), enable_events=True, key='-minstart-')],
        [sg.Text('Duration')],
        [sg.Text('hr'), sg.Input('', size=(3,1), enable_events=True, key='-hrdur-',), sg.Text('min'), sg.Input('', size=(3,1), enable_events=True, key='-mindur-')],
        [sg.Button('SUBMIT',pad=(0,10))],   
    ]

    layout = [
        [
            sg.Column(leftCol),
            sg.VSep(),
            sg.Column(rightCol)
        ]
    ]
    
    window = sg.Window('Jira Timesheets', layout)

    while True:
        event, values = window.read()   
        if event == sg.WIN_CLOSED:
            break
        if event == 'NEW ISSUE':
            shr, smin = 9, 30
            if len(lVals) > 0:
                prev = lVals[-1]
                shr, smin = prev.startHr + prev.getDur()[0], prev.startMin + prev.getDur()[1]
                if smin > 59:
                    smin -= 60
                    shr += 1
            lVals.append(IssueInfo('None', '...', shr, smin, 1))
            lVals = sortIssuesByStartTime(lVals)
            lb = window['-lb-']
            lb.update(values=lVals)
        if event == 'DEL ISSUE':
            if selectedIssue != None:
                lVals.remove(selectedIssue)
                selectedIssue = None
            elif len(lVals) > 0:
                lVals.pop() 

            lb = window['-lb-']
            lb.update(values=lVals)
        if event == 'SETTINGS':
            window.hide()
            settingsPage(settings)
            window.un_hide()
        if event == '-lb-':
            try:
                selectedIssue = values['-lb-'][0]
                if selectedIssue:
                    window['-code-'].Update(selectedIssue.code)
                    window['-comment-'].Update(selectedIssue.comment)
                    window['-hrstart-'].Update(selectedIssue.startHr)
                    window['-minstart-'].Update(selectedIssue.startMin)
                    d = selectedIssue.getDur()
                    window['-hrdur-'].Update(d[0])
                    window['-mindur-'].Update(d[1])
            except IndexError:
                pass
        if event in ['-code-', '-comment-', '-hrstart-', '-minstart-', '-hrdur-', '-mindur-']:
                #print(values['-code-'])
                if selectedIssue:
                    try:
                        selectedIssue.code  = values['-code-'] if values['-code-'] != '' else 'None'
                        selectedIssue.comment = values['-comment-'] if values['-comment-'] != '' else '...'
                        selectedIssue.startHr = int(values['-hrstart-']) if values['-hrstart-'].isdigit() else 0
                        selectedIssue.startMin = int(values['-minstart-']) if values['-hrstart-'].isdigit() else 0
                        selectedIssue.setDur(int(values['-hrdur-']) if values['-hrdur-'].isdigit() else 0, int(values['-mindur-']) if values['-mindur-'].isdigit() else 0)
                        window['-lb-'].Update(values=lVals)
                    except Exception as e:                        
                        messagebox("Error!", e)
                    finally:
                        lVals = sortIssuesByStartTime(lVals)
                        lb = window['-lb-']
                        lb.update(values=lVals)

        if event == 'SUBMIT':
            days:list[int] = []
            apiKey:str = settings.apikey
            email:str = settings.email

            # awfully verbose but basically combines email and api key and decodes them
            authToken = (base64.b64encode((f'{email}:{apiKey}').encode())).decode()
            startDay:int = None
            endDay:int = None
            month:int = None

            try:
                #print(values)
                d1 = window['-startDay-'].DisplayText.split()[0].split('-')
                d2 = window['-endDay-'].DisplayText.split()[0].split('-')
                
                startDay = int(d1[2])
                endDay = int(d2[2])
                month = int(d1[1])
                year = int(d1[0])

                if startDay > endDay:
                    startDay, endDay = endDay, startDay
                
                for i in range(startDay, endDay + 1):
                    if datetime.datetime(year, month, i).weekday() in [5, 6]:
                        continue
                    else:                    
                        days.append(i)


                #print(f'{days}, {month}')
                if settings.testmode:
                    TestAuth(lVals, authToken)
                else:
                    Run(month, days, lVals, authToken)
                
            except Exception as e:
                messagebox("Error!", e)          

    # end of execution
    window.close()

'''
    Entrypoint into the app
'''
if __name__ == '__main__':

    main()
    input()
    quit()
