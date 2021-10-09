from classes import *
import os, sys, subprocess
import socket, threading, time, re
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog as fd
from build.gui import *
from cryptography.fernet import Fernet
from datetime import datetime
from random import randint


IDENTIFICATION_PORT = 9100
DATA_TRANSFER_PORT = 9090
DEVICE_IP = socket.gethostbyname(socket.gethostname())

interfaces = []
devices = []
names = []
viable_devices = []
threads = []
file_list = []

pinged = beaconThread('', IDENTIFICATION_PORT)
pinged.start()

receiver = receivingThread2(DEVICE_IP, DATA_TRANSFER_PORT)
receiver.start()

for device in os.popen('arp -a'): interfaces.append(device)

for blank in interfaces:
  m = re.search('(192\.168\.\d+\.\d+)', blank)
  if m:
    if not m.group(1).split(".")[3] in ("1", "255"):
      a = address(socket.getfqdn(m.group(1)), m.group(1))
      devices.append(a)

threads = []
for potential in devices:
  t1 = probingThread(potential, viable_devices, IDENTIFICATION_PORT)
  t1.start()
  threads.append(t1)

for thread in threads:
  thread.join()

for i in viable_devices:
  names.append(i.getName())


window = Tk()

def getIPbyName(name):
  return (viable_devices[names.index(name)]).getAddr()


def start_data_transfer():
  current_time = datetime.now()
  temp_filename = current_time.strftime("%m/%d/%Y_%H:%M:%S_package")

  tar = tarfile.open(temp_filename, mode="w:gz")
  
  key = Fernet.generate_key()
  for file in file_list:
    tar.add(file)  
  sender = sendingThread(getIPbyName(Users.get()), DATA_TRANSFER_PORT,
             tar, bool(Enc_state.get()), bool(Cmp_state.get()), key)
  sender.start()

  file_list.clear()
  queue_list.delete(0, END)


def load_file(destination):
  for i in fd.askopenfilenames(parent=window, title="Choose the files to send"):
    destination.append(i)
    queue_list.insert(END, os.path.basename(i))


window.geometry("525x550")
window.configure(bg = "#F9F5F3")

canvas = Canvas(
  window,
  bg = "#F9F5F3",
  height = 600,
  width = 525,
  bd = 0,
  highlightthickness = 0,
  relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
  file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
  34.00000000000001,
  33.00000000000006,
  image=image_image_1
)


canvas.create_text(
  158.0,
  17.000000000000057,
  anchor="nw",
  text="bitBybit",
  fill="#22223B",
  font=("Montserrat SemiBold", 36 * -1)
)

canvas.create_text(
  23.000000000000007,
  107.00000000000006,
  anchor="nw",
  text="Nearby Devices",
  fill="#4A4E69",
  font=("Montserrat SemiBold", 14 * -1)
)

canvas.create_text(
  23.000000000000007,
  236.00000000000006,
  anchor="nw",
  text="Message Delivery",
  fill="#4A4E69",
  font=("Montserrat SemiBold", 14 * -1)
)

canvas.create_text(
  300.0,
  236.00000000000006,
  anchor="nw",
  text="File Share",
  fill="#4A4E69",
  font=("Montserrat SemiBold", 14 * -1)
)

canvas.create_rectangle(
  18.000000000000007,
  136.00000000000006,
  277.0,
  163.00000000000006,
  fill="#C4C4C4",
  outline=""
)

#Custom Elements
Enc_state = IntVar()
encryption = Checkbutton(window, text='Encrypt Data', variable=Enc_state, onvalue=1, offvalue=0)
encryption.place(
  x=18.000000000000007,
  y=430.00000000000006,
)

Cmp_state = IntVar()
compression = Checkbutton(window, text='Compress Data', variable=Cmp_state, onvalue=1, offvalue=0)
compression.place(
  x=18.000000000000007,
  y=455.00000000000006,
)

default = StringVar()
default.set("none")
Users = ttk.Combobox(
  canvas,
  textvariable=default,
  values=names
  )
Users.place(
  x=20.0,
  y=138.00000000000006,
  width=255.0,
  height=23.0
)

entry_image_1 = PhotoImage(
  file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
  136.0,
  335.50000000000006,
  image=entry_image_1
)
entry_1 = Text(
  bd=0,
  bg="#C4C4C4",
  highlightthickness=0
)
entry_1.place(
  x=28.000000000000007,
  y=265.00000000000006,
  width=216.0,
  height=139.0
)

# File Label
scrollbar = Scrollbar(canvas)
queue_list = Listbox(canvas, yscrollcommand = scrollbar.set)

queue_list.place(
  x=297,
  y=269.00000000000006,
  width=161.0,
  height=133.0
)
scrollbar.place(
  x=460,
  y=269.00000000000006,
  width=39.0,
  height=133.0
)

canvas.create_rectangle(
  293.0,
  265.00000000000006,
  496.0,
  406.00000000000006,
  fill="#C4C4C4",
  outline="")

#label element
result = Label(canvas, text = "")

result.place(x = 350, y = 425, width = 160, height = 100)

button_image_1 = PhotoImage(
  file=relative_to_assets("button_1.png"))
button_1 = Button(
  image=button_image_1,
  borderwidth=0,
  highlightthickness=0,
  command=start_data_transfer,
  relief="flat"
)
button_1.place(
  x=176.0,
  y=467.00000000000006,
  width=155.0,
  height=35.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: load_file(file_list),
    relief="flat"
)
button_2.place(
    x=388.0,
    y=238.00000000000006,
    width=86.0,
    height=17.0
)
window.resizable(False, False)
window.mainloop()
