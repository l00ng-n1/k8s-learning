import re
import os
import warnings

import pikepdf
import fitz

warnings.filterwarnings("ignore", category=UserWarning)

pattern = re.compile(r'\d')
pattern1 = re.compile(r'pdf')
pattern2 = re.compile(r'enctyp')

for file in os.listdir('.'):
    if pattern.search(file):
        for file1 in os.listdir('.\\'+ file):
            if file1.endswith('.pdf'):
                try:
                    with pikepdf.open('.\\'+ file +'\\'+file1) as pdf:
                        print("PDF未加密。")
                except pikepdf._core.PasswordError:
                    try:
                        with pikepdf.open('.\\'+ file +'\\'+file1, password="Magedu@M61!") as pdf:
                            if os.path.exists('.\\' + file + '\\' + 'new_' + file1) != True:
                                pdf.save('.\\'+ file +'\\'+'enctyp_'+file1)

                                # 去水印
                                doc = fitz.open('.\\'+ file +'\\'+'enctyp_'+file1)
                                for page_num in range(len(doc)):
                                    page = doc[page_num]
                                    images = page.get_images(full=True)

                                    for img in images:
                                        xref = img[0]
                                        img_details = doc.extract_image(xref)
                                        img_width = img_details["width"]
                                        img_height = img_details["height"]

                                        if (img_width, img_height) in [(434, 228), (400, 200)]:
                                            page.delete_image(xref)

                                doc.save('.\\'+ file +'\\'+'new_'+file1)

                                doc.close()
                                os.remove('.\\' + file + '\\' + 'enctyp_' + file1)
                                print('水印去除')


                                print("PDF 解密成功，已保存未加密版本。")
                            else:
                                print("PDF 解密存在。")
                    except pikepdf._core.PasswordError:
                        print('.\\'+ file +'\\'+'enctyp_'+file1+',密码错误。')
                except FileNotFoundError:
                    print("skipping")



