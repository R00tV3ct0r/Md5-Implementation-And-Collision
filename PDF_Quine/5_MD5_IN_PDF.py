# sources : https://github.com/adrien1018/universal-pdf-md5-collision/
# My work is base on the collision-1 and collision-2 files from adrien1018's repository.
# I encurage you to studie the same way I did to really understand whats behind a collisions attack 
# and how to implemente a collision attack in a PDF file.
# The code is written by me with the help of IA in rare occasions.


import argparse, subprocess, os, re, struct, zlib, hashlib
from pypdf import PdfReader
from pypdf.generic import ArrayObject, StreamObject, ContentStream
from io import BytesIO

def pdfstr(s):
    # literal charactere strings must be in parantheses in a PDF with some charactere escaped
    e = s.encode('cp1252', 'replace')
    return b"(" + e.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"

def stream(n, data):
    # Return the stream of the data
    return b"%d 0 obj\n<</Length %d>>\nstream\n" % (n, len(data)) + data + b"\nendstream\nendobj\n"

def ser(o):
    b = BytesIO()
    o.write_to_stream(b)
    return b.getvalue()

def main():
    ap = argparse.ArgumentParser(description="Create a PDF file that contains his own hash (1 page only)")
    ap.add_argument('input')
    ap.add_argument('-o', '--output')
    ap.add_argument('--msg', default="Md5 of this document : ", help='Message to display; default : "Md5 of this document : " ')
    ap.add_argument('--posx', default="center", help='horizontal position from the left size; default : center ')
    ap.add_argument('--posy', default=8, help="vertical position from the bottom; default : 8")
    ap.add_argument('--color', choices=['black', 'white'], default='black', help="text color in ['black', 'white']")
    a = ap.parse_args()
    if a.output is None:
        a.output = os.path.splitext(a.input)[0] + "_md5.pdf"

    c1 = open("collisions-1", 'rb').read()
    c2 = open("collisions-2", 'rb').read()

    # -------------------normalisation of the pdf----------------------

    r = subprocess.run(['qpdf', '--object-streams=disable', '--compress-streams=y', '--force-version=1.7', a.input, 'simplified.pdf'], capture_output=True, text=True)
    if r.returncode == 2 or not os.path.exists("simplified.pdf"):
        print(f"ERROR : {r.stderr}")
        exit()
    elif r.returncode == 3:
        print("ERROR CODE 2 : File created with qpdf but may be corrupted")

    simplified = open("simplified.pdf", "rb").read()

    # rb = raw byte
    # (?m) = multi line
    # ^ = a chaque ligne
    # (\d+) = one or multiple number 
    # (.*?) = every char 
    # re.S = (.*?) accept /n 
    list_objs = {int(m[1]) : m[2] for m in re.finditer(rb'(?m)^(\d+) 0 obj\n(.*?)endobj\n', simplified, re.S)}

    if not list_objs:
        print("obj is empty")
        exit()
    elif max(list_objs) > 997:
        print("ERRROR : PDF to complex more than 997 obj alredy created")
        exit()

    rd = PdfReader(BytesIO(simplified))
    if len(rd.pages) > 1:
        print("number of page superior at 1, keep only the first one and continue")

    page = rd.pages[0]

    # ------------------ Balence the content of the page ---------------------

    contents = page['/Contents']

    # could be Array of object or just one object
    if isinstance(contents, ArrayObject):
        paths = [x.get_object() for x in contents]
    else:
        paths = [contents]
    
    content_data = b"\n".join(path.get_data() for path in paths)

    # Have content_data balance (as many q than Q) :
    so = StreamObject(); so.set_data(content_data)
    depth = minimum = open_EMC = 0
    for _, operateur in ContentStream(so, None).operations:
        if operateur == b'q': 
            depth += 1
        elif operateur == b'Q': 
            depth -= 1
            minimum = min(minimum, depth)
        elif operateur in (b'BMC', b'BDC'): 
            open_EMC += 1
        elif operateur == b'EMC': 
            open_EMC -= 1

    content_data_balance = b"q\n" * (1 - minimum) + content_data + b"\n" + b"EMC\n" * max(0, open_EMC) + b"Q\n" * (1 - minimum + depth)

    # ------------------------ Add the mediabox in the pdf --------------------
    mediabox = page.mediabox
    left, bottom, right = float(mediabox.left), float(mediabox.bottom), float(mediabox.right)
    wide = right - left
    label = a.msg

    # calcul size of the police
    # with a margin of 20 on each size
    # 0.6 * (len(label) + 32 egual the wide of the text for each point in size so max size is 17,5 for the default message
    police_size = round(min(10.0, (wide - 40) / (0.6 * (len(label) + 32))), 1)
    caratere_wide = 0.6 * police_size   

    if a.posx == "center":  
        total_caratere_wide = (len(label) + 32) * caratere_wide                  
        x = left + (wide - total_caratere_wide) / 2        
    else:
        x = int(a.posx)

    y = bottom + int(a.posy)   

    if a.color == "white":
        color = b"1 1 1"
    elif a.color == "black":
        color = b"0 0 0"         

        # we keep the initia pdf and we add the new text and stream
        before = content_data_balance + b"\n/GQz gs\n"
        # BT/ET open and close a text object
        # Tf set the font and size 
        # rg the color (format : "R G B")
        # Td set the position of the text (format : "x y Td") 
        # Tj show the text (format : "(text)Tj")
    before += (b"BT\n/FQz %f Tf\n" % police_size + color + b" rg\n" + b"%f %f Td\n" % (x, y) + pdfstr(label) + b"Tj\nET\n" 
            b"BT\n/FQz %f Tf\n" % police_size + color + b" rg\n" + b"%f %f Td\n" % (x + len(label) * caratere_wide, y))
    after = b"ET\n"

    # ------------------------ reconstruct the Ressource table ------------------
    ressources = page.get('/Resources', {})
    if ressources is not None:
        ressources = ressources.get_object()
    else:
        ressources = {}

    
    def merged(key, extra):
        if hasattr(ressources, 'get'):
            sub = ressources.get(key) 
        else:
            sub = None

        if sub is not None:
            sub = sub.get_object() 
        else:
            sub = {}

        return b"".join(ser(k) + b" " + ser(v) for k, v in sub.items()) + extra

    rb = b"<<"
    for index, values in ressources.items():
        if index == '/Font':
            rb += b"/Font<<" + merged('/Font', b"/FQz 3001 0 R") + b">>"
        elif index == '/ExtGState':
            rb += b"/ExtGState<<" + merged('/ExtGState', b"/GQz 3003 0 R") + b">>"
        else:
            rb += ser(index) + b" " + ser(values)

    if '/Font' not in ressources:
        rb += b"/Font<</FQz 3001 0 R>>"
    if '/ExtGState' not in ressources:
        rb += b"/ExtGState<</GQz 3003 0 R>>"
    rb += b">>"

    # ------------------- object 999 -------------------
    # 192 = prefix + obj 1000; 32 caratere * 16 possibility; 128 = size of a collion paire
    prefix = c1[:192 + 32 * 16 * 128]

    skip = {'/Type', '/Contents', '/Parent', '/Resources', '/StructParents', '/MediaBox'}
    tail = b"\n3000 0 R]/MediaBox" + ser(mediabox)

    for index, values in page.items():
        if index not in skip:
            tail += ser(index) + b" " + ser(values)

    tail += b"/Parent 998 0 R/Resources" + rb + b">>\nendobj\n"

    construct_file = bytearray(prefix + tail)
    pos_obj = {999: prefix.index(b'999 0 obj')}

    def add(n, body):
        pos_obj[n] = len(construct_file)
        construct_file.extend(body)

    # new catalog 
    root = rd.trailer['/Root']
    drop = {'/Pages', '/Type', '/Version', '/StructTreeRoot', '/MarkInfo', '/Outlines', '/Names', '/Dests', '/OpenAction', '/AcroForm', '/Threads'}
    catalog = b"".join(ser(index) + b" " + ser(values) for index, values in root.items() if index not in drop)

    add(998, b"998 0 obj\n<</Type/Pages/Count 1/Kids[999 0 R]>>\nendobj\n")
    add(997, b"997 0 obj\n<</Type/Catalog/Pages 998 0 R" + catalog + b">>\nendobj\n")
    add(1000, stream(1000, before))

    for i in range(32):
        for j in range(16):
            n = (i * 16 + j) * 2 + 1002
            add(n, stream(n, b"(%x)Tj " % j))
            add(n + 1, b"%d 0 obj\n<</Length 0>>\nstream\n\nendstream\nendobj\n" % (n + 1))

    add(3000, stream(3000, after))
    add(3001, b"3001 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Courier-Bold/Encoding/WinAnsiEncoding>>\nendobj\n")
    add(3003, b"3003 0 obj\n<</Type/ExtGState/ca 1/CA 1/BM/Normal/SMask/None>>\nendobj\n")

    for n, body in list_objs.items():              
        add(n, b"%d 0 obj\n" % n + body + b"endobj\n")

    # xref table add /W[1 4 2] for every entry, 
    # 1 byte for the type, 4 bytes for the offset, 2 bytes for the generation number
    #-----------------------xref table -----------------
    xref_id = 3004
    size = xref_id + 1
    xoff = len(construct_file)
    rows = b''

    for n in range(size):
        if n == xref_id: 
            rows += struct.pack('>BIH', 1, xoff, 0)
        elif n in pos_obj: 
            rows += struct.pack('>BIH', 1, pos_obj[n], 0)
        else: 
            rows += struct.pack('>BIH', 0, 0, 65535 if n == 0 else 0)

    compression = zlib.compress(rows, 9)

    trailer = simplified[simplified.rfind(b'trailer'):]
    extra = b""
    m = re.search(rb'/Info (\d+) 0 R', trailer)

    if m: 
        extra += b"/Info %s 0 R" % m[1]

    m = re.search(rb'/ID \[(<[0-9a-f]+><[0-9a-f]+>)\]', trailer)

    if m: 
        extra += b"/ID[%s]" % m[1]

    # /XRef stock the compress entry ans startxref show his start position,
    # %%EOF end of the pdf
    construct_file += (b"%d 0 obj\n<</Type/XRef/Size %d/W[1 4 2]/Root 997 0 R%s/Filter/FlateDecode/Length %d>>\nstream\n"
        % (xref_id, size, extra, len(compression))) + compression
    construct_file += b"\nendstream\nendobj\nstartxref\n%d\n%%%%EOF\n" % xoff
    construct_file = bytes(construct_file)

    # -------------- add the hash value -----------------
    nhash = hashlib.md5(construct_file).hexdigest()
    data = construct_file[:192]

    for i in range(32):
        res_digit = int(nhash[i], 16)
        for j in range(16):
            pos = i * 16 + j
            data += (c1 if j == res_digit else c2)[192 + 128 * pos: 192 + 128 * (pos + 1)]

    data += construct_file[len(data):]
    open(a.output, 'wb').write(data)


if __name__ == '__main__':
    main()