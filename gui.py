import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter.ttk as ttk
import pdfannots.gui_classes as gui
import pdfannots.utils as utils
import os
import json
import re


def execute_pdf_annot(pdf_location = ['tests/periodo_simples.pdf'],export = 'output/'):
    anotacoes = {}
    os.mkdir("temp/")
    if os.path.exists(export) == False:
        os.mkdir(export)
    
    anotacao_path = "temp/anotacao.json"
    for pdf in pdf_location:
        os.system("python pdfannots.py " + pdf_location + " -f json --cols 1 -o" + anotacao_path)

        pdf_file_name = re.sub(".*\\\\","",pdf)
        pdf_file_name = re.sub("[.]pdf$","",pdf_file_name)

        anotacoes_file = open(anotacao_path,mode='r')

        anotacoes[pdf] = json.loads(anotacoes_file.read())
        anotacoes_file.close()

        utils.image_extract(annotations=anotacoes[pdf],pdf_file=pdf,location="temp/output")

        anotacao_reordenada = utils.annots_reorder_columns(annotations=anotacoes[pdf],columns=3,tolerance=0.1)

        file = open(export+pdf_file_name+'.md', 'w',encoding='utf-8')
        file_html = open(export+pdf_file_name+'.html', 'w',encoding='utf-8')
        md_print = utils.md_export(annots=anotacao_reordenada)
        html_print = utils.md_export(annots=anotacao_reordenada,template="template_html.html")

        file.write(md_print)
        file.close()
        file_html.write(html_print)
        file_html.close()

    os.rmdir("temp/")
    return anotacoes

    


def gui_interface():

    # root = tk.Tk()

    root = TkinterDnD.Tk()

    root.geometry('800x800')

    root.minsize(width = 600, height = 400)

    def _quit():
        root.quit()
        root.destroy()
        print("BDU fechado")

    
    root.protocol("WM_DELETE_WINDOW", _quit)


    notebook = ttk.Notebook(root)
    # notebook.grid()
    notebook.grid_rowconfigure(1, weight=1)
    notebook.grid_columnconfigure(1, weight=1)

    load_pdf = gui.gui_pdf_load(notebook)

    load_pdf.set_size(width=root.winfo_screenmmwidth(),height=root.winfo_screenmmheight())

    # load_pdf.file_list.drop_target_register(DND_FILES)
    # load_pdf.file_list.dnd_bind('<<Drop>>', lambda e: load_pdf.file_list.insert(tk.END, e.data.sub('\\{','').strip('}')))

    


    root.title = "AAA"
    root.state('zoomed')

    notebook.grid(sticky = "nsew")


    notebook.add(load_pdf.ui,text="File choose")

    notebook.grid_columnconfigure(0,weight=10)

    root.grid_columnconfigure(0,weight=1)

    print(root.winfo_screenwidth())
    # noteb

    root.mainloop()

    print(load_pdf.files)

    root.quit()

if(__name__ == "__main__"):
	gui_interface()