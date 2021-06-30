from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import base64
import requests
import datetime
import _thread


class TaskAdmin():
    def __init__(self, api):
        self.users = {"sunny": "1151444784998780", "nidhi": "1137973327976671",
                      "andy": "1151443707130528", "sam": "1199535753095509",
                      "abhinav": "1200143632350982", "gaurav": "831530689871554",
                      "reena": "1151444074847557"}
        self.token = '1/1151444784998780:d48b663e9ef79b24f4a41012febcc6ac'
        self.projects = {"1": "1168596845982757",
                         "2": "1200303919365069", "3": "1126636209528890"}
        self.url = 'https://app.asana.com/api/1.0/tasks'
        self.headers = {"Authorization": f"Bearer {self.token}",
                        "content-type": "application/json"}
        self.api = api
        self.files = []
        self.defaultProjectID = "1126636209528890"

    def getGDrive(self):
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:

            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            gauth.flow.params.update({'approval_prompt': 'force'})

            gauth.LocalWebserverAuth()

        elif gauth.access_token_expired:
            gauth.Refresh()

        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile("mycreds.txt")

        drive = GoogleDrive(gauth)
        return drive

    def uploadFileToGDrive(self, filename):
        try:
            drive = self.getGDrive()
            folder = drive.ListFile(
                {'q': f"title='WhatsAppUploads' and trashed=false and mimeType='application/vnd.google-apps.folder'"}).GetList()[0]
            file = drive.CreateFile(
                {'title': f'{filename}', 'parents': [{'id': folder['id']}]})
            file.SetContentFile("uploads/"+filename)
            file.Upload()
            return f"https://drive.google.com/open?id={file['id']}"
        except Exception as e:
            print(e)

    def downloadTaskFile(self, uri, ext):
        result = self.api.driver.execute_async_script("""
        var uri = arguments[0];
        var callback = arguments[1];
        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'arraybuffer';
        xhr.onload = function(){ callback(toBase64(xhr.response)) };
        xhr.onerror = function(){ callback(xhr.status) };
        xhr.open('GET', uri);
        xhr.send();
        """, uri)
        if result.isdigit():
            raise Exception("Request failed with status %s" % result)
        bytes = base64.b64decode(result)
        filename = str(datetime.datetime.now()).replace(
            ":", "-").replace(".", "-")+"."+ext
        with open("uploads/"+filename, 'wb') as file:
            file.write(bytes)
        link = self.uploadFileToGDrive(filename)
        self.files.append(link)

    def getTasksFromWhatsapp(self):
        unReadMessages = self.api.getUnreadMessages('Task-Admin')
        self.files = []
        task = []
        flag = False
        for message in unReadMessages:
            if message['Type'].strip() == 'Text':
                if message["Text"] == "Ss":
                    flag = True

            if flag and message.get("Text") != 'Ss' and message.get("Text") != 'Ee':
                task.append(message)
        return task

    def getLinksInHTML(self, html_notes):
        html = ""
        for idx, link in enumerate(html_notes):
            if link != "":
                html += f"<li><a href='{link}'>File {idx+1}</a></li>"
        html = f"<body><ul>{html}</ul></body>"
        return html

    def prepareTaskForAsana(self, task):
        taskDetails = {}
        taskDetails["data"] = {}
        name = ""
        for msg in task:
            Type = msg.get("Type")

            if Type == "Text":
                if msg.get("Text").lower() in self.users:
                    taskDetails["data"]["assignee"] = self.users.get(
                        msg.get("Text").lower())

                elif msg.get("Text").isdigit():
                    taskDetails["data"]["projects"] = []
                    taskDetails["data"]["projects"].append(
                        self.projects.get(msg.get("Text")))

                else:
                    name += msg.get("Text")+" "
                    taskDetails["data"]["name"] = name

            if Type == "Image":
                self.downloadTaskFile(msg.get("Image"), "jpeg")
#                 _thread.start_new_thread(self.downloadTaskFile,(msg.get("Image"), "jpeg"),)

            if Type == "Audio":
                self.downloadTaskFile(msg.get("Src"), "mp3")
#                 _thread.start_new_thread(self.downloadTaskFile,(msg.get("Src"), "mp3",))

        if len(self.files) > 0:
            taskDetails["data"]["html_notes"] = self.files
        return taskDetails

    def uploadTaskToAsana(self, task):
        try:
            html_notes = task["data"].get("html_notes", [])
            projects = task["data"].get("projects")
            if len(html_notes) > 0:
                task["data"]["html_notes"] = self.getLinksInHTML(html_notes)
            if not projects:
                task["data"]["projects"] = []
                task["data"]["projects"].append(self.defaultProjectID)
            result = requests.post(self.url, headers=self.headers, json=task)
            if result.status_code == 201:
                print("\n[*] Task Uploaded...")
                sentBox = self.api.driver.find_element_by_css_selector(
                    ".vR1LG._3wXwX.copyable-area")
                inputBox = sentBox.find_element_by_css_selector(
                    "._2_1wd.copyable-text.selectable-text")
                inputBox.send_keys("Task Uploaded!!")
                sentBtn = sentBox.find_element_by_css_selector("._1E0Oz")
                sentBtn.click()
            else:
                print("Task upload failed!")
        except Exception as error:
            print("Task upload failed!, ", error)
