# Import statements
import os
import tkinter as tk
import tkinter.ttk as ttk
import sv_ttk # Created by github user rbende
from tkinter import BooleanVar, filedialog
from PIL import Image, ImageTk
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)






# Custom classes =======================================================================================================================================================

# NavigableCanvas class
class NavigableCanvas(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        xscrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        yscrollbar = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='NSEW')
        xscrollbar.grid(row=1, column=0, sticky='EW')
        yscrollbar.grid(row=0, column=1, sticky='NS')
    

    def show_image(self, file):
        self.canvas.delete('all')
        img = ImageTk.PhotoImage(file)
        self.canvas.create_image((0, 0), anchor='nw', image=img)
        self.canvas.image = img
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


# ScrollableFrame class
class ScrollableFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        canvas = tk.Canvas(self)
        self.frame = ttk.Frame(canvas)
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)

        canvas.configure(yscrollcommand=self.scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='both')
        self._frame_id = canvas.create_window((0, 0), anchor='nw', window=self.frame)

        self.frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(self._frame_id, width=canvas.winfo_width() - 4))


# QueueItem class
class QueueItem(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        # Main frame
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)


        # Select file frame
        self.select_file_Frm = ttk.Frame(self, borderwidth=1, relief='raised')
        self.select_file_Frm.columnconfigure(1, weight=1)
        self.select_file_Frm.columnconfigure(1, weight=1)
        self.select_file_Frm.grid(row=0, column=0, sticky='EW')

        # Select file frame contents
        self.select_file_Btn = ttk.Button(self.select_file_Frm, text="Select File", command=self.select_file)
        self.select_file_Btn.grid(row=0, column=0, padx=[5, 0], pady=5)
        self.filepath_Ent = ttk.Entry(self.select_file_Frm)
        self.filepath_Ent.grid(row=0, column=1, padx=5, pady=5, sticky='EW')


        # "Convert to" label
        self.convert_to_Lbl = ttk.Label(self, text="convert to")
        self.convert_to_Lbl.grid(row=0, column=1, padx=5)


        # Conversion formats menu
        self.converted = False
        self.supported_formats = {
            'PNG':                      ['PNG',     '.png',     'RGB'],
            'PNG (Transparent PNG)':    ['PNG',     '.png',     'RGBA'],
            'JPG':                      ['JPG',     '.jpg',     'RGB'],
            'JPEG':                     ['JPEG',    '.jpeg',    'RGB'],
            'BMP':                      ['BMP',     '.bmp',     'RGBA'],
            'TIF':                      ['TIF',     '.tif',     'RGBA'],
            'TIFF':                     ['TIFF',    '.tiff',    'RGBA'],
            'WEBP':                     ['WEBP',    '.webp',    'RGBA'],
            'GIF':                      ['GIF',     '.gif',     'RGBA'],
            'JPG (CMYK)':               ['JPG',     '.jpg',     'CMYK'],
            'JPEG (CMYK)':              ['JPEG',    '.jpeg',    'CMYK'],
            'TIF (CMYK)':               ['TIF',     '.tif',     'CMYK'],
            'TIFF (CMYK)':              ['TIFF',    '.tiff',    'CMYK']
        }
        self.selected_format = tk.StringVar()
        self.selected_format.trace('w', self.format_selected)
        self.format_menu_Btn = ttk.Menubutton(self, width=5, text=" . . . ")

        formats_Mnu = tk.Menu(self.format_menu_Btn, tearoff=False)
        for format in self.supported_formats:
            formats_Mnu.add_radiobutton(label=format, value=self.supported_formats.get(format), variable=self.selected_format)

        self.format_menu_Btn['menu'] = formats_Mnu
        self.format_menu_Btn.grid(row=0, column=2)


        # Delete item button
        self.delete_item_Btn = tk.Button(self, text="\u2573", borderwidth=0, state='disabled', command=self.destroy)
        self.delete_item_Btn.bind('<Enter>', self.show_delete_button)
        self.delete_item_Btn.bind('<Leave>', self.hide_delete_button)
        self.delete_item_Btn.grid(row=0, column=4, padx= [10, 1], pady=[0, 1])

    
    # Select file
    def select_file(self):
        filepath = filedialog.askopenfilename(title="Select a File")
        if not filepath:
            return
        else:
            self.filepath_Ent.delete(0, 'end')
            self.filepath_Ent.insert(0, filepath.replace("{", "").replace("}", ""))

    
    # Conversion format selected
    def format_selected(self, *args):
        self.filepath = self.filepath_Ent.get()
        self.format_menu_Btn.configure(text=self.selected_format.get().split()[0])
        convert_Btn.configure(state='normal')
    

    # Convert file
    def convert_file(self):
        # Setup
        self.filepath_Ent.configure(state='readonly')
        self.convert_to_Lbl.configure(text=f"convert to {self.selected_format.get().split()[0]}", width=15)
        column_width = self.select_file_Btn.winfo_width() + 10
        self.columnconfigure(2, minsize=column_width)
        progressbar = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        increment = column_width / 4
        self.format_menu_Btn.destroy()
        self.select_file_Btn.destroy()
        progressbar.grid(row=0, column=2, padx=[5, 0], sticky='EW')

        # Conversion
        file = Image.open(self.filepath)
        self.filename = file.filename[0:file.filename.rindex(".")]
        file = file.convert('RGBA')
        background = Image.new('RGBA', file.size, (255, 255, 255))
        progressbar['value'] += increment
        file_alpha_composite = Image.alpha_composite(background, file)
        progressbar['value'] += increment
        self.converted_file = file_alpha_composite.convert(self.selected_format.get().split()[2])
        progressbar['value'] += increment
        self.converted = True
        progressbar['value'] += increment
        convert_Btn.configure(state='disabled')

        # Show preview/download button
        progressbar.destroy()
        preview_Btn = ttk.Button(self.select_file_Frm, text="Preview", command=self.preview_file).grid(row=0, column=0, padx=[5, 0], pady=5)
        self.download_ver = 0
        self.download_Btn = ttk.Button(self, text="DOWNLOAD", style='Accent.TButton', command=self.download)
        self.download_Btn.grid(row=0, column=2, sticky='EW')
        if auto_download.get() == True:
            self.download()


    # Preview file
    def preview_file(self):
        file_viewer_Frm.show_image(self.converted_file)


    # Download file
    def download(self):
        format = self.selected_format.get().split()[1]
        if self.download_ver == 0:
            if not os.path.exists(f"{self.filename}{format}"):
                self.converted_file.save(f"{self.filename}{format}")
            else:
                self.download_ver += 1
                while os.path.exists(f"{self.filename} ({self.download_ver}){format}"):
                    self.download_ver += 1
                self.converted_file.save(f"{self.filename} ({self.download_ver}){format}")
            self.download_Btn.destroy()
            self.additional_downloads_Btn = ttk.Button(self, text=f"Download ({self.download_ver + 1})", command=self.download)
            self.additional_downloads_Btn.grid(row=0, column=2, padx=[5, 0], sticky='EW')
        else:
            while os.path.exists(f"{self.filename} ({self.download_ver}){format}"):
                    self.download_ver += 1
            self.converted_file.save(f"{self.filename} ({self.download_ver}){format}")
            self.additional_downloads_Btn.configure(text=f"Download ({self.download_ver + 1})")
        self.download_ver += 1
            

    # Show delete item button
    def show_delete_button(self, e):
        self.delete_item_Btn.configure(state='normal')

    # Hide delete item button
    def hide_delete_button(self, e):
        self.delete_item_Btn.configure(state='disabled')






# Functions =======================================================================================================================================================

# Add queue item
def add_queue_items():
    filepaths = filedialog.askopenfilenames(title="Select a File")
    if not filepaths:
        QueueItem(queue_Frm.frame).pack(fill='x', expand=True, padx=5, pady=5)
    else:
        for file in filepaths:
            item = QueueItem(queue_Frm.frame)
            item.pack(fill='x', expand=True, padx=5, pady=5)
            item.filepath_Ent.delete(0, 'end')
            item.filepath_Ent.insert(0, file)


# Convert all queued files
def convert():
    for item in queue_Frm.frame.winfo_children():
        if item.filepath_Ent.get() and item.selected_format.get() != "" and item.converted == False:
            item.convert_file()


# Download all
def download_all():
    for item in queue_Frm.frame.winfo_children():
        item.download()


# Clear all
def clear_all():
    warning_Msb = tk.messagebox.askokcancel("Confirm Clear", 'Clicking "OK" will clear all files in the queue. Do you wish to proceed?', icon='warning')
    if warning_Msb == True:
        for item in queue_Frm.frame.winfo_children():
            item.destroy()


# Center main window
def center_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 1350
    window_height = 750
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    window.geometry(f'1350x750+{x_coordinate}+{y_coordinate}')






# Main window =======================================================================================================================================================

# Main window
root = tk.Tk()
sv_ttk.set_theme('light')
root.title("Image File Converter")

root.minsize(1350, 750)
root.rowconfigure(0, weight=1, minsize=750)
root.columnconfigure([0, 1], weight=1, minsize=550)
root.columnconfigure(2, minsize=250)
center_window(root)


# Sizegrip
sizegrip_SzG = ttk.Sizegrip(root).grid(row=0, column=2, sticky='SE')






# File viewer frame =======================================================================================================================================================

# File viewer frame
file_viewer_Frm = NavigableCanvas(root, borderwidth=1, relief='raised')
file_viewer_Frm.grid(row=0, column=0, sticky='NSEW', padx=[10, 5], pady=10)






# File converter frame =======================================================================================================================================================

# File converter frame
file_converter_Frm = ttk.Frame(root)
file_converter_Frm.rowconfigure(0, weight=1)
file_converter_Frm.columnconfigure(0, weight=1)
file_converter_Frm.grid(row=0, column=1, padx=5, pady=10, sticky='NSEW')


# Queue frame
queue_Frm = ScrollableFrame(file_converter_Frm, borderwidth=1, relief='raised')
queue_Frm.grid(row=0, column=0, sticky='NSEW')


# Action row
actions_Frm = ttk.Frame(file_converter_Frm, borderwidth=1, relief='raised')
actions_Frm.grid(row=1, column=0, pady=[10, 0], sticky='EW')

# Add file button
add_file_Btn = ttk.Button(actions_Frm, text="+", style='Accent.TButton', command=add_queue_items)
add_file_Btn.pack(side='left', padx=5, pady=5, ipadx=12)

# Convert button
convert_Btn = ttk.Button(actions_Frm, text="CONVERT", style='Accent.TButton', state='disabled', command=convert)
convert_Btn.pack(side='right', padx=[10, 5], pady=5)

# Download all button
download_all_Btn = ttk.Button(actions_Frm, text="Download All", command=download_all).pack(side='right')

# Clear all button
clear_all_Btn = ttk.Button(actions_Frm, text="Clear", command=clear_all).pack(side='right', padx=10)






# Settings frame =======================================================================================================================================================

# Settings frame
settings_Frm = ttk.Frame(root, borderwidth=1, relief='solid')
settings_Frm.grid(row=0, column=2, padx=[5, 10], pady=10, sticky='NSEW')


auto_download = BooleanVar()
auto_download_Chk = ttk.Checkbutton(settings_Frm, style='Switch.TCheckbutton', onvalue=True, offvalue=False, variable=auto_download).grid(row=0, column=0, padx=5, pady=5)
auto_download_Lbl = ttk.Label(settings_Frm, text="Auto-download").grid(row=0, column=1, pady=5)






# Display main window =======================================================================================================================================================

# Add initial queue item
QueueItem(queue_Frm.frame).pack(fill='x', expand=True, padx=5, pady=5)


# Display main window
root.mainloop()