import tkinter

class OptionBox(tkinter.Toplevel):
    def __init__(self, parent, title, options):
        tkinter.Toplevel.__init__(self, parent)
        self.title(title)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.options = options
        self.result: str
        frmQuestion = tkinter.Frame(self)
        tkinter.Label(frmQuestion, text="Select one of these options").grid()
        frmQuestion.grid(row=1)
        frmButtons = tkinter.Frame(self)
        frmButtons.grid(row=2)
        column = 0
        for option in self.options:
            btn = tkinter.Button(
                frmButtons, 
                text=option, 
                command=lambda x=option:self.setOption(x))
            btn.grid(column=column,row=0)
            column += 1
        # self.eval(f'tk::PlaceWindow . center')
        self.grab_set()
        self.wait_window()

    def setOption(self, optionSelected):
        self.result = optionSelected
        self.destroy()
    def cancel(self):
        self.result = "cancel"
        self.destroy()