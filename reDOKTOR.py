import tkinter as tk
import struct
from tkinter import filedialog

lvl_arr = []
lvl_ents = []

lvl = b""

root = tk.Tk()
path = filedialog.askopenfilename(initialdir=".", title="Select file", filetypes=(("cld files", "*.cld"),))

with open(path, "rb") as f:
    lvl = f.read()

hint_size = struct.unpack("I", lvl[:4])[0]
hint = lvl[4:4+hint_size].decode()
print(f"hint: {hint}")
lvl=lvl[4+hint_size:]

wtf, ballz_appear = struct.unpack("II", lvl[:8])
lvl=lvl[4+4*4:]
metallic_features = struct.unpack("I"*wtf, lvl[:4*wtf])
if wtf < 9:
    metallic_features = tuple(list(metallic_features)+[0]*(9-wtf))
print(metallic_features, ballz_appear)
lvl=lvl[4*wtf +10*4*2:]

wtf2_size = struct.unpack("I", lvl[:4])[0]
lvl=lvl[4:]
print(wtf2_size)
for i in range(wtf2_size):
    dat0, dat1, dat2_size = struct.unpack("III", lvl[:4*3])
    lvl=lvl[4*3:]
    for j in range(dat2_size):
        data = struct.unpack("I"*8, lvl[:4*8])
        text = lvl[4*8:4*8+data[7]].decode()
        lvl=lvl[4*8+data[7]:]
        print(data[:-1], text)
        lvl_ents.append((data[:-1], text))
        print('---')

dimensions = struct.unpack("II", lvl[:8])
lvl=lvl[8:]
for i in range(dimensions[0]):
    tmp=[]
    for j in range(dimensions[1]):
        tmp.append(struct.unpack("i"*6, lvl[:6*4]))
        lvl=lvl[6*4:]
    lvl_arr.append(tmp)

print(lvl_arr)
print(lvl_ents)

"""
0 - синий
1 - зелёный
2 - красный
3 - жёлтый
4 - серый
5 - бирюзовый
6 - розовый железный?
7 - коричневый железный?
8 - фиолетовый железный?
---
100 - радужный
101 - Кирпич
102 - ?
103 - бобм
104 - ?
105 - ебучая хуйня
106 - крест
"""
POSSIBLE_LEVEL_PRIZES = [
    (-1, "Empty"),
    (0, "Blue"),
    (1, "Green"),
    (2, "Red"),
    (3, "Yellow"),
    (4, "Gray"),
    (5, "Turquoise"),
    (6, "Pink"),
    (7, "Brown"),
    (8, "Violet"),
    (100, "Rainbow"),
    (101, "Brick"),
    (102, "102"),
    (103, "Bobm"),
    (104, "104"),
    (105, "FF XIII: Lightning Returns"),
    (106, "Holy Cross"),
]

POSSIBLE_LEVEL_PRIZES_STRINGS = tuple([i[1] for i in POSSIBLE_LEVEL_PRIZES])
POSSIBLE_LEVEL_ENT_TYPE = ("BALL", "BALL?", "->", "<-", "/\\", "\\/")


def get_string(ent: tuple):
    if ent[0] != 0 and ent[0] != 1:
        return POSSIBLE_LEVEL_ENT_TYPE[ent[0]]
    if ent[3] == -1:
        return ""
    if ent[1]:
        return "X"
    chained, metallic= "", ""
    if ent[2]:
        chained="C"
    if ent[5]:
        metallic="M"
    if ent[3] == 100:
        return "GAY"
    elif ent[3] == 101:
        return "[]"
    elif ent[3] == 102:
        return "102"
    elif ent[3] == 103:
        return "BOBM"
    elif ent[3] == 104:
        return "104"
    elif ent[3] == 105:
        return "LIGHT"
    elif ent[3] == 106:
        return "+"
    return f"{chained}O{metallic}"

buttons = []
ents_buttons = []

class EditLevelGrid(tk.Toplevel):
    def __init__(self, i: int, j: int):
        tk.Toplevel.__init__(self)

        self.wm_title(f"{i}_{j}")

        self.coords = (i, j)
        data = lvl_arr[i][j]
        print(data, data[0])

        tk.Label(self, text=f"{i:02d} {j:02d}", font="fixedsys").pack(pady=5)

        # 0 - ent type
        tk.Label(self, text="Ent Type").pack()
        self.POSSIBLE_LEVEL_ENT_TYPE_VARS = tk.StringVar(value=POSSIBLE_LEVEL_ENT_TYPE)
        self.ent_type = tk.Listbox(self, listvariable=self.POSSIBLE_LEVEL_ENT_TYPE_VARS, height=6, exportselection=0)
        self.ent_type.selection_set(data[0])
        self.ent_type.see(data[0])
        self.ent_type.pack()

        # 1 - hidden
        self.hidden_state = tk.IntVar()
        self.hidden_state.set(data[1])
        self.hidden_box = tk.Checkbutton(self, text="Hidden", variable=self.hidden_state, onvalue=1, offvalue=0)
        self.hidden_box.pack()

        #print(data, data[1], self.hidden_state.get())

        # 2 - chains
        self.chain_state = tk.IntVar()
        self.chain_state.set(data[2])
        self.chain_box = tk.Checkbutton(self, text="Chained", variable=self.chain_state, onvalue=1, offvalue=0)
        self.chain_box.pack()

        # 3 - ball colour
        tk.Label(self, text="Colour (Ball&!Metallic)").pack()
        self.list_ent_svars = tk.StringVar(value=POSSIBLE_LEVEL_PRIZES_STRINGS)
        self.list_ent = tk.Listbox(self, listvariable=self.list_ent_svars, exportselection=0)
        for e in range(len(POSSIBLE_LEVEL_PRIZES)):
            if POSSIBLE_LEVEL_PRIZES[e][0] == data[3]:
                self.list_ent.selection_set(e)
                self.list_ent.see(e)
        self.list_ent.pack()

        # 5
        self.f_state = tk.IntVar()
        self.f_state.set(data[5])
        self.f_box = tk.Checkbutton(self, text="Metallic", variable=self.f_state, onvalue=1, offvalue=0)
        self.f_box.pack()

        self.save = tk.Button(self, text="Save&Close", command=self.exit_save)
        self.save.pack(side=tk.RIGHT)

        self.close = tk.Button(self, text="Close", command=self.destroy)
        self.close.pack(side=tk.RIGHT)

    def exit_save(self):
        i, j = self.coords
        data = (self.ent_type.curselection()[0], self.hidden_state.get(), self.chain_state.get(), POSSIBLE_LEVEL_PRIZES[self.list_ent.curselection()[0]][0], 0, self.f_state.get())
        lvl_arr[i][j] = data
        print(data)

        fg="white"
        bg="black"
        if (data[0] == 0 or data[0] == 1) and  10 > data[3] >= 0:
                    fg=POSSIBLE_LEVEL_PRIZES[data[3]+1][1].lower()
        if data[1]:
            fg="red"
            bg="white"
        buttons[(i*20)+j].config(text=get_string(data), fg=fg, bg=bg)
        
        self.destroy()

class EditLevelEntity(tk.Toplevel):
    def __init__(self, i: int):
        tk.Toplevel.__init__(self)

        self.idx = i

        data = lvl_ents[i]
        print(data)

        tk.Label(self, text="Texture name").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.insert(0, data[1])
        self.name_entry.pack()

        self.data0 = tk.Entry(self)
        self.data0.insert(0, data[0][0])
        self.data0.pack()

        tk.Label(self, text="X Coord").pack()
        self.x_coord = tk.Entry(self)
        self.x_coord.insert(0, data[0][1])
        self.x_coord.pack()

        tk.Label(self, text="Y Coord").pack()
        self.y_coord = tk.Entry(self)
        self.y_coord.insert(0, data[0][2])
        self.y_coord.pack()

        self.data3 = tk.Entry(self)
        self.data3.insert(0, data[0][3])
        self.data3.pack()

        self.data4 = tk.Entry(self)
        self.data4.insert(0, data[0][4])
        self.data4.pack()

        # exit no?
        tk.Label(self, text="Exit No.").pack()
        self.data5 = tk.Entry(self)
        self.data5.insert(0, data[0][5])
        self.data5.pack()

        self.data6 = tk.Entry(self)
        self.data6.insert(0, data[0][6])
        self.data6.pack()

        #print(data, data[1], self.hidden_state.get())

        self.save = tk.Button(self, text="Save&Close", command=self.exit_save)
        self.save.pack(side=tk.RIGHT)

        self.close = tk.Button(self, text="Close", command=self.destroy)
        self.close.pack(side=tk.RIGHT)

    def exit_save(self):
        i = self.idx
        #data = lvl_ents[i]
        texture_name = self.name_entry.get()
        lvl_ents[i] = (tuple([int(i.get()) for i in [self.data0, self.x_coord, self.y_coord, self.data3, self.data4, self.data5, self.data6]]), texture_name)
        ents_buttons[i].config(text=texture_name)
        self.destroy()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_metallic_frame(self):
        self.metallic_frame = tk.Frame(self.left_frame, relief=tk.RAISED, borderwidth=1)
        self.metallic_label = tk.Label(self.metallic_frame, text="Half-Metall")
        self.metallic_label.pack()

        self.metallic_vars = []
        self.metallic_buttons = []
        for i in range(9):
            self.metallic_vars.append(tk.IntVar())
            self.metallic_vars[-1].set(metallic_features[i])
            self.metallic_buttons.append(tk.Checkbutton(self.metallic_frame, text=POSSIBLE_LEVEL_PRIZES[i+1][1], variable=self.metallic_vars[-1], onvalue=1, offvalue=0))
            self.metallic_buttons[-1].pack()

    def save_cld(self):
        o = bytearray()
        o += struct.pack("I", len(hint.encode()))
        o += hint.encode()

        metallic_features = [self.metallic_vars[i].get() for i in range(9)]

        #write metallic features
        o += struct.pack("II", len(metallic_features), int(self.number_ballz.get()))
        o += b'\0'*4*(4-1) # figured out spawning
        o += struct.pack("I"*len(metallic_features), *metallic_features)
        o += b'\0'*10*4*2

        #todo figure out why it's like that...
        o += struct.pack("I", 1)
        for i in range(1):
            o += b'\0'*4*2
            o += struct.pack("I", len(lvl_ents))
            for j in range(len(lvl_ents)):
                #flags+data
                o += struct.pack("I"*7, *lvl_ents[j][0])
                #texture name
                o += struct.pack("I", len(lvl_ents[j][1].encode()))
                o += lvl_ents[j][1].encode()

        o += struct.pack("II", 20, 20)
        for i in range(20):
            for j in range(20):
                o += struct.pack("i"*6, *lvl_arr[i][j])

        save_path = filedialog.asksaveasfilename(initialdir=".", title="Where to save", filetypes=(("cld files", "*.cld"),))

        with open(save_path, "wb") as f:
            f.write(o)

        print("SAVED!")
        

    def create_widgets(self):
        global buttons

        self.button_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.button_frame.grid(row=0, column=1)

        for i in range(20):
            for j in range(20):
                ent = lvl_arr[i][j]
                fg="white"
                bg="black"
                if ent[1]:
                    fg="red"
                    bg="white"
                command = lambda a=i, b=j: EditLevelGrid(a, b)

                if ent[0] == 0:
                    if 10 > ent[3] >= 0:
                        fg=POSSIBLE_LEVEL_PRIZES[ent[3]+1][1].lower()
                    elif ent[3] == 100:
                        fg="gold"
                    elif ent[3] == 101:
                        fg="brown"
                    elif ent[3] == 102:
                        # TODO: find it being used?
                        pass
                    elif ent[3] == 103:
                        fg="white"
                    elif ent[3] == 104:
                        # TODO: find it being used?
                        pass
                    elif ent[3] == 105:
                        fg="violet"
                    elif ent[3] == 106:
                        fg="yellow"

                buttons.append(tk.Button(self.button_frame, fg=fg, bg=bg, text=get_string(ent), command=command, height=2, width=4, font='fixedsys'))
                buttons[-1].grid(row=j, column=i)
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0)
        self.ents_frame = tk.Frame(self.left_frame, relief=tk.RAISED, borderwidth=1)
        self.ents_frame.pack()

        for e in range(len(lvl_ents)):
            data, text = lvl_ents[e]
            ents_buttons.append(tk.Button(self.ents_frame, text=text, command=lambda a=e: EditLevelEntity(a)))
            ents_buttons[-1].pack(padx=5, pady=5)

        self.create_metallic_frame()
        self.metallic_frame.pack()

        self.number_ballz_frame = tk.Frame(self.left_frame, relief=tk.RAISED, borderwidth=1)
        self.number_ballz_frame.pack()
        tk.Label(self.number_ballz_frame, text="Number of balls to appear").pack()
        self.number_ballz = tk.Entry(self.number_ballz_frame)
        self.number_ballz.insert(0, str(ballz_appear))
        self.number_ballz.pack()

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=1, column=1)
        
        #self.save_json_btn = tk.Button(self.bottom_frame, text="Load CLD", command=self.load_cld)
        #self.save_json_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.save_cld_btn = tk.Button(self.bottom_frame, text="Save CLD", command=self.save_cld)
        self.save_cld_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        #self.save_json_btn.grid(row=1, column=1)

app = Application(master=root)
app.mainloop()
