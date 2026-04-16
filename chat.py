from openai import OpenAI
from tkinter import *
from tkinter import ttk

global content

root=Tk()
frm = ttk.Frame(root, padding = 100)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()
btn = ttk.Button(frm, ...)
print(btn.configure().keys())


def addToContent(newContent):
    content += newContent

#client = OpenAI()

#response = client.chat.completions.create(
#    model = "gpt-5.4-mini",
#    messages = [
#        {"role": "system", "content": "You are a professional low baller"}, #This is what you are telling the system to
#        {"role": "user", "content": ""}                                     #This is what the user is asking the system to do
#    ]
#)

#print(response.choices[0].message.content)