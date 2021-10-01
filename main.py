from classes import *
import os, sys, subprocess
import socket, threading, time, re
from tkinter import *
from tkinter import ttk
from build.gui import *


IDENTIFICATION_PORT = 9100
DATA_TRANSFER_PORT = 9090

interfaces = []
devices = []
names = []
viable_devices = []
threads = []

pinged = beaconThread('', IDENTIFICATION_PORT)
pinged.start()

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

window.geometry("525x600")
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
  text="LocalShare",
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

canvas.create_rectangle(
  293.0,
  265.00000000000006,
  483.0,
  406.00000000000006,
  fill="#C4C4C4",
  outline="")

button_image_1 = PhotoImage(
  file=relative_to_assets("button_1.png"))
button_1 = Button(
  image=button_image_1,
  borderwidth=0,
  highlightthickness=0,
  command=lambda: print("button_1 clicked"),
  relief="flat"
)
button_1.place(
  x=176.0,
  y=467.00000000000006,
  width=155.0,
  height=35.0
)

window.resizable(False, False)
window.mainloop()
