import tkinter

class OptionBox(tkinter.Toplevel):
    def __init__(self, obj, title, options):
        self.obj = obj
        tkinter.Toplevel.__init__(self, self.obj.window)
        n_columns = len(options)

        self.resizable(width=True, height=True)
        self.title(title)
        self.transient(self.obj.window)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.options = options
        self.result: str

        label = tkinter.Label(self, text="Select one of these options")
        label_width = label.winfo_reqwidth()
        h = label.winfo_reqheight()
        btn = []
        btn_widths = []
        for i, option in enumerate(self.options):
            btn.append(
                tkinter.Button(
                    self,
                    text=option,
                    command=lambda x=option:self.setOption(x)
                )
            )
            btn_widths.append(btn[-1].winfo_reqwidth())

        btn_pad_x = 20

        total_width = sum(btn_widths) + 2 * n_columns * btn_pad_x
        total_height = 4 * h

        label.grid(row=0, column=0, columnspan=n_columns, padx=(total_width-label_width)//2, pady=h//2)
        for i in range(n_columns):
            btn[i].grid(row=1, column=i, padx=btn_pad_x, pady=h//2)


        x = (self.obj.window_width - total_width) // 2
        y = (self.obj.window_height - total_height) // 2
        self.geometry('{}x{}+{}+{}'.format(total_width, total_height, x, y))

        self.grab_set()
        self.wait_window()

    def setOption(self, optionSelected):
        self.result = optionSelected
        self.destroy()
    def cancel(self):
        self.result = "cancel"
        self.destroy()