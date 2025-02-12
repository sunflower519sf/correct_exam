# from pypdf import PdfReader

# reader = PdfReader("example.pdf")
# for page in reader.pages:
#     for image in page.images:
#         with open(image.name, "wb") as fp:
#             fp.write(image.data)

import os
import fitz  # pip install --upgrade pip; pip install --upgrade pymupdf
from tqdm import tqdm # pip install tqdm

workdir = "./img"

for each_path in os.listdir(workdir):
    if ".pdf" in each_path:
        doc = fitz.Document((os.path.join(workdir, each_path)))

        for i in tqdm(range(len(doc)), desc="pages"):
            for img in tqdm(doc.get_page_images(i), desc="page_images"):
                xref = img[0]
                image = doc.extract_image(xref)
                pix = fitz.Pixmap(doc, xref)
                pix.save(os.path.join(workdir, "%s_p%s-%s.png" % (each_path[:-4], i, xref)))
                
print("Done!")


