import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import pdfannots.utils as utils
import re
import json
import shutil


class gui_interface():
    def __init__(self, master = None) -> None:
        self.__master = master
        self.ui = ttk.Frame(self.__master)

    



class gui_pdf_load(gui_interface):
    def __init__(self, master = None) -> None:
        self.__master = master
        self.ui = tk.Frame(self.__master)

        self.set_size()
        self.assets_import()
        self.basic_ui()
        self.basic_ui_draw()
        self.basic_ui_commmands()

    def assets_import(self):
        self.icon_delete = tk.PhotoImage(file = "pdfannots/gui_assets/delete.png")
        self.icon_trash = tk.PhotoImage(file = "pdfannots/gui_assets/trash.png")
       
    def basic_ui(self):
        self.column_1 = tk.Frame(self.ui,highlightbackground="blue", highlightthickness=2)
        self.column_2 = tk.Frame(self.ui,highlightbackground="green", highlightthickness=2)
        self.file_list = tk.Listbox(self.column_1)
        self.btn_file_selector = ttk.Button(self.column_1,text="Select files")
        self.btn_pdf_export = ttk.Button(self.column_1, text = "Export PDF highlights")

        # Grid com atalhos para remover item selecionado ou todos
        self.column_btns = ttk.Frame(self.column_1)
        self.btn_remove_item = ttk.Button(self.column_btns,image=self.icon_delete)
        self.btn_remove_all = ttk.Button(self.column_btns,image=self.icon_trash)

        self.parameters_tab = ttk.Frame(self.column_2)
        self.parameters_label = ttk.Label(self.parameters_tab,text = "Adicione parametros")
        self.parameters_entry = ttk.Entry(self.parameters_tab)

    def basic_ui_draw(self):
        self.column_1.grid(column = 1, row = 1,sticky='nwse')
        self.column_2.grid(column = 2, row = 1,sticky='nwse')
        self.file_list.grid(column = 1, row = 1, columnspan = 3,sticky = "nwse")
        self.btn_file_selector.grid(column=1,row = 2,sticky = "nwse")
        self.btn_pdf_export.grid(column=2,row = 2,sticky = "nwse")
        self.ui.grid_columnconfigure(1,weight=7)
        self.ui.grid_columnconfigure(2,weight=3)

        self.column_btns.grid(column=4,row=1,rowspan=2)
        self.btn_remove_item.grid()
        self.btn_remove_all.grid()

        self.column_1.grid_columnconfigure(1,weight=3)
        self.column_1.grid_columnconfigure(2,weight=3)
        self.column_1.grid_columnconfigure(3,weight=6)


        self.column_2.grid_columnconfigure(0,weight=1)


        self.parameters_tab.grid(column = 0, row = 0,sticky = "nwse")
        self.parameters_label.grid(sticky = "nwse")
        self.parameters_entry.grid(sticky = "nwse")

    def basic_ui_commmands(self):
        self.btn_file_selector['command'] = self.add_file
        self.btn_remove_all["command"] = self.remove_all
        self.btn_remove_item["command"] = self.remove_file
        self.btn_pdf_export["command"] = self.export_folder

    def export_folder(self):
        self.files = list(self.file_list.get(0,tk.END))
        print(self.files)

        if len(self.files) >= 1:
            self.folder = filedialog.askdirectory(title="Select export folder")
            # self.folder = str(os.path.abspath(self.folder))
            
            self.pdf_export(pdf_location=self.files,export = self.folder)
        else:
            messagebox.showerror(title = "Select at least one PDF file.",
            message = "You have to select at least one PDF file on the <Select files> button.")

    def add_file(self):
        file_open = filedialog.askopenfiles(defaultextension=['pdf'],filetypes=[('PDF','.pdf')])
        if isinstance(file_open,list):
            for i in file_open:
                path = str(os.path.abspath(i.name))
                # self.file_list
                self.file_list.insert("end", path)

    def remove_all(self):
        self.file_list.delete(0,tk.END)
    
    def remove_file(self):
        selected_items = self.file_list.curselection()
        for item in selected_items:
            print(item)
            self.file_list.delete(item)

    def set_size(self,width = 500, height = 500):
        self.width = width
        self.height = height

    def pdf_export(self,pdf_location = [], export = 'output'):
        anotacoes = {}
        if os.path.exists("temp/") == False:
            os.mkdir("temp/")
        if os.path.exists(export) == False:
            os.mkdir(export)
        
        anotacao_path = "temp/anotacao.json"
        for pdf in pdf_location:
            os.system("python pdfannots.py " + pdf + " -f json --cols 1 -o" + anotacao_path)
            pdf = re.sub("\\\\","/",pdf)

            pdf_file_name = re.sub(".*/","",pdf)
            pdf_file_name = re.sub("[.]pdf$","",pdf_file_name)

            anotacoes_file = open(anotacao_path,mode='r')

            anotacoes[pdf] = json.loads(anotacoes_file.read())
            anotacoes_file.close()

            if len(anotacoes[pdf]) > 0:
                utils.image_extract(annotations=anotacoes[pdf],pdf_file=pdf,location=export)

                anotacao_reordenada = utils.annots_reorder_columns(annotations=anotacoes[pdf],columns=3,tolerance=0.1)

                file = open(export+"/"+pdf_file_name+'.md', 'w',encoding='utf-8')
                file_html = open(export+"/"+pdf_file_name+'.html', 'w',encoding='utf-8')
                md_print = utils.md_export(annots=anotacao_reordenada)
                html_print = utils.md_export(annots=anotacao_reordenada,template="template_html.html")

                file.write(md_print)
                file.close()
                file_html.write(html_print)
                file_html.close()
            else:
                print("Empty file.")

        shutil.rmtree("temp/")






