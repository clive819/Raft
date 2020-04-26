from raft import Raft
import tkinter as tk

if __name__ == '__main__':
    raft = Raft()

    window = tk.Tk()
    window.resizable(False, False)
    window.title("Raft Demo")

    keyLabel = tk.Label(master=window, text='Key')
    keyLabel.grid(row=0, column=0, padx=5, pady=5, sticky='nse')

    keyEntry = tk.Entry(master=window, width=10)
    keyEntry.grid(row=0, column=1, pady=5, sticky='nsew')

    toggleBtn = tk.Button(master=window, text='Start Server')
    toggleBtn.grid(row=0, column=2, columnspan=2, pady=5, sticky='nsew')

    valLabel = tk.Label(master=window, text='Value')
    valLabel.grid(row=1, column=0, padx=5, pady=5, sticky='nse')

    valEntry = tk.Entry(master=window, width=10)
    valEntry.grid(row=1, column=1, pady=5, sticky='nsew')

    sendBtn = tk.Button(master=window, text='Send', command=raft.commit)
    sendBtn.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')

    retrieveBtn = tk.Button(master=window, text='Retrieve', command=raft.retrieveFroKey)
    retrieveBtn.grid(row=1, column=3, padx=5, pady=5, sticky='nsew')

    log = tk.Text(master=window, state=tk.DISABLED, width=20, height=20)
    log.grid(row=2, column=0, columnspan=4, sticky='nsew')

    toggleBtn.config(command=lambda: raft.toggleServer(window, keyEntry, valEntry, toggleBtn, log))

    window.mainloop()
