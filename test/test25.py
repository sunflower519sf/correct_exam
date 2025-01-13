import os
import fitz  # PyMuPDF

# 指定要處理的檔案名稱
pdf_file = "test.pdf"  # 請將此替換為你的檔案名稱
workdir = "./img"  # 請將此替換為你的工作目錄

# 確保檔案存在
pdf_path = os.path.join(workdir, pdf_file)
if os.path.exists(pdf_path):
    doc = fitz.Document(pdf_path)
    os.makedirs(workdir, exist_ok=True)
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            pix.save(os.path.join(workdir, "%s_p%s-%s.png" % (pdf_file[:-4], i, xref)))
            
else:
    print(f"檔案 {pdf_file} 不存在，請確認路徑是否正確。")
