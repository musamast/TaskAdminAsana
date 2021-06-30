import whatsappApi
import taskAdmin

api = whatsappApi.WhatsappApi()
print("\n[*] Opening https://web.whatsapp.com/")


print("\n[*] Scan QR code to continue...")
while True:
    sidePage = api.driver.find_elements_by_class_name("_3U29Q")
    if len(sidePage) != 0:
        break
print("\n[*] Starting Task admin...")
admin = taskAdmin.TaskAdmin(api)
print("\n[*] Checking for tasks...")
while True:
    try:
        if api.isChatUnRead("Task-Admin"):
            if api.getChatLastMessageText("Task-Admin") == "Ee":
                print("\n[*] New task found...")
                task = admin.getTasksFromWhatsapp()
                print("\n[*] Fetching task details...")
                taskDetails = admin.prepareTaskForAsana(task)
                print("\n[*] Uploading task to Asana...")
                admin.uploadTaskToAsana(taskDetails)
                api.openDefaultChat()
    except Exception as error:
        print(error)
