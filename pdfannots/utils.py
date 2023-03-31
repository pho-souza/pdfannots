import datetime
import typing as typ
import colorsys
import pathlib
import os
import fitz
import re
import operator

from jinja2 import Environment, FileSystemLoader

CHARACTER_SUBSTITUTIONS = {
    'ﬀ': 'ff',
    'ﬁ': 'fi',
    'ﬂ': 'fl',
    'ﬃ': 'ffi',
    'ﬄ': 'ffl',
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"',
    '…': '...',
}

DEFAULT_COLOR = (1,1,0)

PATH = pathlib.Path(__file__).resolve().parent / 'templates'
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(str(PATH)),
    trim_blocks=True,
    lstrip_blocks=False
)

DEFAULT_TEMPLATE = "template_default.md"




def cleanup_text(text: str) -> str:
    """
    Normalise line endings and replace common special characters with plain ASCII equivalents.
    """
    if '\r' in text:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
    return ''.join([CHARACTER_SUBSTITUTIONS.get(c, c) for c in text])


def merge_lines(captured_text: str, remove_hyphens: bool = False, strip_space: bool = True) -> str:
    """
    Merge and cleanup lines in captured text, optionally removing hyphens.

    Any number of consecutive newlines is replaced by a single space, unless the
    prior line ends in a hyphen, in which case they are just removed entirely.
    This makes it easier for the renderer to "broadcast" newlines to active
    annotations regardless of box hits. (Detecting paragraph breaks is tricky,
    and left for future work!)
    """
    results = []

    lines = captured_text.splitlines()
    for i in range(len(lines)):
        thisline = lines[i]
        if thisline == '':
            continue

        nextline = lines[i + 1] if i + 1 < len(lines) else None

        if (len(thisline) >= 2
                and thisline[-1] == '-'       # Line ends in an apparent hyphen
                and thisline[-2].islower()):  # Prior character was a lowercase letter
            # We have a likely hyphen. Remove it if desired.
            if remove_hyphens:
                thisline = thisline[:-1]
        elif (not thisline[-1].isspace()
              and nextline is not None
              and (nextline == '' or not nextline[0].isspace())):
            # Insert space to replace the line break
            thisline += ' '

        results.append(cleanup_text(thisline))

    if results and strip_space:
        results[0] = results[0].lstrip()
        results[-1] = results[-1].rstrip()

    return ''.join(results)


def decode_datetime(dts: str) -> typ.Optional[datetime.datetime]:
    if dts.startswith('D:'):  # seems 'optional but recommended'
        dts = dts[2:]
    dts = dts.replace("'", '')
    zi = dts.find('Z')
    if zi != -1:  # sometimes it's Z/Z0000
        dts = dts[:zi] + '+0000'
    fmt = '%Y%m%d%H%M%S'
    # dates in PDFs are quite flaky and underspecified... so perhaps worth defensive code here
    for suf in ['%z', '']:  # sometimes timezone is missing
        try:
            return datetime.datetime.strptime(dts, fmt + suf)
        except ValueError:
            continue
    return None

def convert_to_hls(colors: list) -> tuple:
    """
    Convert rgb colors to hsl color pattern 
    
    """
    # print(isinstance(colors, list))
    if isinstance(colors, list) and len(colors) == 3:
        (r, g, b) = colors
    else:
        (r, g, b) = DEFAULT_COLOR
    (h,l,s) = colorsys.rgb_to_hls(r,g,b)
    return (h,l,s)

def colors_names(colors_hls: tuple) -> str:
    """
    The colors name intervals are from mgmeyers: https://github.com/mgmeyers/pdfannots2json
    """
    if len(colors_hls) != 3:
        return "none"
    else:
        (h,l,s) = colors_hls
        if l < 0.12:
            return "Black"
        if l > 0.98:
            return "White"
        if s < 0.2:
            return "Gray"
        if h < 15/360:
            return "Red"
        if h < 45/360:
            return "Orange"
        if h < 65/360:
            return "Yellow"
        if h < 160/360:
            return "Green"
        if h < 190/360:
            return "Cyan"
        if h < 265/360:
            return "Blue"
        if h < 280/360:
            return "Purple"
        if h < 320/360:
            return "Pink"
        if h < 335/360:
            return "Magenta"
        return "Red"
        
def md_export(annots,template = DEFAULT_TEMPLATE):
    md_template = TEMPLATE_ENVIRONMENT.get_template(template)
    retorno = md_template.render(title = 'Nota titulo',
    anotacoes = annots)
    return retorno

def image_extract(annotations,pdf_file,location,folder = "img/"):
    """
    Extract images from PDFs using the criteria from annots json

    If positive, add relative img_path and has_image attribute
    """
    file = pdf_file
    pdf_file = fitz.open(file)

    # print(file)

    for annotation in annotations:
        if 'annot_number' not in locals():
            annot_number = 0
        if annotation['type'] == 'Square':
            annot_number = annot_number + 1
            page = annotation['page'] - 1

            pdf_page = pdf_file[page]

            # Remove annotations in the page
            for annot in pdf_page.annots():
                pdf_page.delete_annot(annot)

            user_space = annotation["rect_coord"]
            # area = pdf_page.get_pixmap(dpi = 300)
            area = pdf_page.bound()
            area.x0 = user_space[0]*area[2]
            area.x1 = user_space[2]*area[2]
            area.y0 = (1-user_space[3])*area[3]
            area.y1 = (1-user_space[1])*area[3]

            clip = fitz.Rect(area.tl, area.br)

            # print(clip)

            if not os.path.exists(location):
                os.mkdir(location)
            if not os.path.exists(location+"/"+folder):
                os.mkdir(location+"/"+folder)

            file = re.sub(".*/","",file)
            page = page +1

            file_name = file+"_p"+str(page)+'_'+str(annot_number) + ".png"

            file_export = location+"/"+folder+file_name
            file_export = re.sub("/+","/",file_export)


            # print(pdf_page,' - annotation number: ', annot_number)

            img_folder = folder +  "/" +file_name
            img_folder = re.sub("/+","/",img_folder)

            img = pdf_page.get_pixmap(clip = clip,dpi = 300,)
            img.save(file_export)

            if os.path.exists(file_export):
                annotation['has_img'] = True
                annotation['img_path'] = img_folder
            else:
                annotation['has_img'] = False
                annotation['img_path'] = ""
    pdf_file.close()


def annots_reorder_custom(annotations: dict,criteria = [], ordenation = "asc") -> dict:
    """
    This function reordenate the annotations based on criteria order
    """
    criteria = criteria
    validate_criteria = ["page","type","start_xy","author","created"]
    for i in criteria:
        if i not in validate_criteria:
            print(i," criteria is not valid! Please use: ", str(validate_criteria))
            print(criteria)
            return annotations
    
    # if isinstance(ordenation,list) and len(ordenation) != len(criteria):
    #     print("Ordenation not valid! Please use a list of" + len(criteria) + " strings, or a simple string.")
    #     return annotations

    temp = annotations.copy()

    temp = sorted(temp,key=operator.itemgetter(*criteria))

    return temp


def annots_reorder_columns(annotations: dict,columns = 1,tolerance = 0.1) -> dict:
    """
    This function reordenate the annotations based on: page, columns and vertical position
    """
    temp = []
    # temp2 = []
    
    # Columns size
    columns_x = []
    for i in range(0,columns+1):
        col_widget = (1/columns) * i
        columns_x.append(col_widget)
    
    # Get all values
    pages = []
    rect_coord = []
    index = []
    index_init = 0
    for annotation in annotations:
        index.append(index_init)
        pages.append(annotation['page'])
        rect_coord.append(annotation['rect_coord'])
        index_init = index_init + 1
        annotation['index'] = index_init
    
    pages = set(pages)
    annotation_index_x0 = [-1]
    annotation_index_x1 = [-1]
    # for page in pages:
    #     page_init = len(temp)
    for column in range(1,len(columns_x)):
        for annotation in annotations:
            # if  index not in annotation_index:
            index = annotation['index']
            x0 = annotation['rect_coord'][0]
            x1 = annotation['rect_coord'][2]
            y0 = annotation['rect_coord'][1]
            y1 = annotation['rect_coord'][3]
            annotation["y"] = 1-y0
            column_min = columns_x[column-1] - tolerance
            column_max = columns_x[column] + tolerance
            # print("\n\n\nColumn: ",column,"\n Min: ",column_min,"\nMax: ",column_max)
            if x0 >= column_min and x0 < column_max and index not in annotation_index_x0:
                annotation['column'] = [column]
                annotation_index_x0.append(index)
            if x1 >= column_min and x1 < column_max and index not in annotation_index_x1:
                    annotation['column'].append(column)
                    annotation_index_x1.append(index)

    for annotation in annotations:
        if annotation["column"][0] == annotation["column"][1]:
            annotation["column"] = annotation["column"][0]
        elif annotation["column"][0] == 1:
            annotation["column"] = 1.0
        else:
            annotation["column"] = max(annotation["column"])

    

    
    temp = annotations.copy()
    
    temp = sorted(temp,key=operator.itemgetter('page', 'column',"y"))
                    
    
    return temp
    


    
