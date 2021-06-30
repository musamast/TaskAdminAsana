import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, StaleElementReferenceException)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta

from selenium.webdriver.common.keys import Keys
import time
import _thread


class WhatsappApi():
    def __init__(self):
        chrome_option = Options()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_option.add_experimental_option("prefs", prefs)
        chrome_option.headless = False
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(
            'chromedriver.exe'), options=chrome_option)
        self.driver.maximize_window()
        self.driver.get('https://web.whatsapp.com/')

    def getRecentChatsTitle(self):
        try:
            recentChatsTitle = []
            recentChats = self.driver.find_elements_by_xpath(
                "//div[@id='pane-side']/div/div/div/div")
            for chat in recentChats:
                title = self.getChatTitle(chat)
                if title not in recentChatsTitle:
                    recentChatsTitle.append(title)
            return recentChatsTitle

        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='pane-side']/div/div/div/div"))
            )

    def getAllChatsTitle(self):
        titles = []
        while True:
            recentChatsTitle = self.getRecentChatsTitle()
            for title in recentChatsTitle:
                if title not in titles:
                    titles.append(title)
            self.__scrollDownPaneSide()
            newChatsTitle = self.getRecentChatsTitle()
            if newChatsTitle == recentChatsTitle:
                return titles

    def getRecentChats(self):
        try:
            recentChats = self.driver.find_elements_by_xpath(
                "//div[@id='pane-side']/div/div/div/div")
            return recentChats

        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='pane-side']/div/div/div/div"))
            )

    def getChat(self, title):
        for chat in self.getRecentChats():
            if title == self.getChatTitle(chat):
                return chat

    def scrollToChat(self, title):
        try:
            if self.getcurrentChatTitle() == title:
                for chat in self.getRecentChats():
                    if self.getChatTitle(chat) == title:
                        return chat
            while True:
                recentChats = self.getRecentChats()
                recentChatsTitle = self.getRecentChatsTitle()
                for chat in recentChats:
                    if self.getChatTitle(chat) == title:
                        return chat
                self.__scrollDownPaneSide()
                newChatsTitle = self.getRecentChatsTitle()
                if newChatsTitle == recentChatsTitle:
                    None
        except Exception as error:
            print(error, "scrollToChat")

    def isChatUnRead(self, title):
        try:
            chat = self.getChat(title)
            chat.find_element_by_class_name(
                "_38M1B").get_attribute("aria-label").split(' ')[0]
            return True
        except NoSuchElementException:
            return False

    def getChatUnreadMessageCount(self, title):
        try:
            chat = self.getChat(title)
            count = 0
            if self.isChatUnRead(title):
                count = chat.find_element_by_class_name(
                    "_38M1B").get_attribute("aria-label").split(' ')[0]
                return int(count)
            else:
                return count
        except Exception as error:
            print(error, "Error in getChatUnreadMessageCount()")

    def getChatTitle(self, chat):
        try:
            return chat.find_element_by_class_name("_3Dr46").text
        except Exception as error:
            print(error, "Error in getChatTitle()")

    def getChatLastMessageTimestamp(self, title):
        try:
            chat = self.getChat(title)
            return chat.find_element_by_class_name("_15smv").text
        except Exception as error:
            print(error, "Error in getChatLastMessageTimestamp()")

    def getChatLastMessageSender(self, title):
        try:
            chat = self.getChat(title)
            return chat.find_element_by_css_selector("._2vfYK").text.split("\n")[0]
        except Exception as error:
            print(error)

    def getChatLastMessageText(self, title):
        try:
            chat = self.getChat(title)
            return chat.find_element_by_css_selector("._2vfYK").text.split("\n")[2]
        except IndexError:
            return chat.find_element_by_css_selector("._2vfYK").text.split("\n")[0]
        except Exception as error:
            print(error)

    def getMessageTimestamp(self, message):
        try:
            return message.find_element_by_class_name("UFTvj").text
        except Exception as error:
            print(error, "Error in getMessageTimestamp()")

    def getMessageSender(self, message):
        try:
            title = self.getcurrentChatTitle()
            if not self.isGroupChat(title):
                sender = title
                return sender
            sender = message.find_element_by_css_selector(
                ".copyable-text").get_attribute("data-pre-plain-text")
            return sender.split("]")[-1][1:][:-2]
        except NoSuchElementException:
            sender = message.find_element_by_css_selector("._26iqs").text
            return sender
        except Exception as error:
            print(error, "Error in getMessageSender()")

    def isGroupChat(self, title):
        try:

            chat = self.getChat(title)
            span = chat.find_element_by_class_name(
                "_27MZN").find_element_by_tag_name('span')

            if "group" in span.get_attribute("data-testid"):
                return True
            else:
                return False
        except NoSuchElementException:
            return False

    def getcurrentChatTitle(self):
        try:
            title = self.driver.find_element_by_class_name("_2KQyF").text
            return title
        except NoSuchElementException:
            return None
        except Exception as error:
            print(error, "getcurrentChatTitle()")

    def getMessageData(self, message):
        if "_397qe" in message.get_attribute("class"):
            return {'Type': "Information", 'Text': message.text}
        container = message.find_element_by_class_name("_24wtQ")
        containerClassName = container.get_attribute("class")
        messageInOrOut = ""

        if "message-in" in message.get_attribute("class"):
            messageInOrOut = "Message In"
        elif "message-out" in message.get_attribute("class"):
            messageInOrOut = "Message Out"

        if "_2Ye7z" in containerClassName or "_1uDmw" in containerClassName:
            timestamp = self.getMessageTimestamp(message)
            time.sleep(1)
            src = container.find_element_by_tag_name(
                'audio').get_attribute('src')
            sender = self.getMessageSender(message)
            return {"Type": "Audio", "Src": src, "MessageInOrOut": messageInOrOut, "Timestamp": timestamp, "Sender": sender}

        elif "_2W7I-" in containerClassName:
            messageContainer = message.find_element_by_css_selector(
                "._3-8er.selectable-text.copyable-text")
            messageText = messageContainer.text
            emojies = [i.get_attribute(
                'alt') for i in messageContainer.find_elements_by_tag_name("img")]
            emojies = " ".join(emojies)
            timestamp = self.getMessageTimestamp(message)
            sender = self.getMessageSender(message)
            return {"Type": "Text", "Text": messageText, "Emojis": emojies,
                    "MessageInOrOut": messageInOrOut, "Timestamp": timestamp, "Sender": sender}

        elif len(containerClassName.split()) == 1 or containerClassName.split()[1] == "_1-U5A":
            timestamp = self.getMessageTimestamp(message)
            sender = self.getMessageSender(message)
            return {"Type": "Deleted", "Timestamp": timestamp, "Sender": sender}

        elif "gZ4ft" in containerClassName:
            btn = container.find_element_by_css_selector("._2MfUK")
            val = btn.find_elements_by_css_selector("._2p30Q")[-1]
            img = val.find_element_by_tag_name("img")
            imgSrc = img.get_attribute('src')
            text = img.get_attribute('alt')
            timestamp = self.getMessageTimestamp(message)
            sender = self.getMessageSender(message)
            return {"Type": "Image", "Image": imgSrc, "Text": text,
                    "MessageInOrOut": messageInOrOut, "Timestamp": timestamp, "Sender": sender}

        else:
            print(containerClassName)
            return {"Type": "Unknown"}

    def __scrollDownPaneSide(self, count=3):
        self.driver.find_element_by_id("pane-side").click()
        for i in range(count):
            self.driver.find_element_by_tag_name(
                'body').send_keys(Keys.PAGE_DOWN)

    def __scrollUpPaneSide(self, count=3):
        self.driver.find_element_by_id("pane-side").click()
        for i in range(count):
            self.driver.find_element_by_tag_name(
                'body').send_keys(Keys.PAGE_UP)

    def scrollToRecentChats(self):
        while True:
            recentChatsTitle = self.getRecentChatsTitle()
            self.__scrollUpPaneSide()
            newChatsTitle = self.getRecentChatsTitle()
            if newChatsTitle == recentChatsTitle:
                break

    def __openChat(self, title):
        while True:
            for chatter in self.driver.find_elements_by_xpath("//div[@id='pane-side']/div/div/div/div"):
                chatter_path = ".//span[@title='{}']".format(
                    title)

                # Wait until the chatter box is loaded in DOM
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(@title,'{}')]".format(
                                title)))
                    )
                except StaleElementReferenceException:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(@title,'{}')]".format(
                                title)))
                    )

                try:
                    chatter_name = chatter.find_element_by_xpath(
                        chatter_path).text
                    if chatter_name == title:
                        chatter.find_element_by_xpath(
                            ".//div/div").click()
                        return True
                except Exception as e:
                    pass

    def openDefaultChat(self):
        defaultChat = "+92 318 3525717"
        if not defaultChat in self.getRecentChatsTitle():
            sentBox = self.driver.find_element_by_css_selector(
                ".vR1LG._3wXwX.copyable-area")
            inputBox = sentBox.find_element_by_css_selector(
                "._2_1wd.copyable-text.selectable-text")
            inputBox.send_keys(
                "https://api.whatsapp.com/send?phone=923183525717&text=test")
            sentBtn = sentBox.find_element_by_css_selector("._1E0Oz")
            sentBtn.click()
            lastMsg = self.driver.find_elements_by_css_selector(
                ".message-out")[-1]
            lastMsg.click()
            sentBox = self.driver.find_element_by_css_selector(
                ".vR1LG._3wXwX.copyable-area")
            sentBtn = sentBox.find_element_by_css_selector("._1E0Oz")
            sentBtn.click()
        else:
            self.__openChat(defaultChat)

    def getUnreadMessages(self, title):
        unreadCount = self.getChatUnreadMessageCount(title)
        self.__openChat(title)
        unreadMessages = []
        time.sleep(1)
        for i in self.driver.find_elements_by_css_selector(
                ".GDTQm.message-in.focusable-list-item"):
            data = self.getMessageData(i)
            if data not in unreadMessages:
                dataID = i.get_attribute("data-id")
                if dataID is not None and "album" in dataID:
                    for k in i.find_elements_by_class_name("_2IsiC"):
                        unreadMessages.append(self.getMessageData(k))
                else:
                    unreadMessages.append(data)

        try:
            self.driver.find_element_by_class_name("_3P-mY").click()
        except NoSuchElementException:
            print("_3P-mY Not Found")

        time.sleep(2)
        for i in self.driver.find_elements_by_css_selector(
                ".GDTQm.message-in.focusable-list-item"):
            data = self.getMessageData(i)
            if data not in unreadMessages:
                unreadMessages.append(data)
        print("unreadCount: ", unreadCount)
        print("Messages Found: ", len(unreadMessages))
        messages = unreadMessages[-unreadCount:]
        return messages
