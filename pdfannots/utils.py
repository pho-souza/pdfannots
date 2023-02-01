import datetime
import typing as typ
import colorsys

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

def convert_to_hls(colors: tuple) -> tuple:
    """
    Convert rgb colors to hsl color pattern 
    
    """
    if isinstance(colors, tuple) and len(colors) == 3:
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
        if h < 170/360:
            return "Green"
        if h < 190/360:
            return "Cyan"
        if h < 263/360:
            return "Blue"
        if h < 280/360:
            return "Purple"
        if h < 335/360:
            return "Magenta"
        return "Red"
        
