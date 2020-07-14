import time
import logging
import requests
from bs4 import BeautifulSoup
from enum_new import LIST_LINK_RES_CLASS
from enum_new import RESTAURANT_NAME_CLASS
from enum_new import RESTAURANT_VIEW_CLASS
from enum_new import RESTAURANT_SERVICE_CLASS
from enum_new import RESTAURANT_ADDRESS_CLASS
from enum_new import RESTAURANT_IMG_RES_CLASS
from enum_new import RESTAURANT_REVIEW_1_CLASS
from enum_new import RESTAURANT_REVIEW_2_CLASS
from enum_new import RESTAURANT_COMMENT_1_CLASS
from enum_new import RESTAURANT_COMMENT_2_CLASS
from enum_new import RESTAURANT_COMMENT_IMAGE_CLASS
from alchemy import Restaurant, Comment, RestaurantImage, CommentImage, Service
from alchemy import insert_res, insert_ser, insert_res_img, insert_res_ser, insert_com_img, insert_com, get_categories


class ControllerRestaurant:

    def __init__(self):
        self.base_url = "https://www.yelp.com"

    def list_link_restaurant(self):
        """
        vao trong tung category Lay ra danh sach cac link truy cap cua tung nha hang

        :return: danh sach link cac nha hang va loai cua chung
        """
        list_url = []
        categories = get_categories()
        for category in categories:
            url = self.base_url + "/search?cflt=" + category.name
            get_page = requests.get(url)
            html_page = BeautifulSoup(get_page.text, 'html.parser')
            result = html_page.find_all(class_=LIST_LINK_RES_CLASS)
            try:
                for item in result:
                    if item['href'][1:4] == "biz":
                        list_url.append([item['href'], category.id])
                    else:
                        pass
            except:
                pass
            time.sleep(7.5)
        return list_url

    def restaurant(self, list_url):
        """
        vao trong chi tiet nha hang loc ra cac thong tin can thiet de luu vao db

        :param list_url: danh sach link cua cac nha hang
        :return: da thuc hien xong ham
        """
        for url in list_url:
            try:
                res = Restaurant()
                cmt = Comment()
                res_img = []
                url_page = self.base_url + url[0]
                get_page = requests.get(url_page)
                html_page = BeautifulSoup(get_page.text, 'html.parser')

                result_1 = html_page.find_all(class_=RESTAURANT_IMG_RES_CLASS)
                # lay anh
                if result_1 is not None or result_1 != []:
                    for item in result_1:
                        temp = item.find('img')
                        image_r = RestaurantImage()
                        image_r.image = temp['src']
                        res_img.append(image_r)
                else:
                    pass
                # lay ten
                result_2 = html_page.find(class_=RESTAURANT_NAME_CLASS)
                res.name = result_2.text.replace("'", "/@/")
                # lay dia chi
                adr = ""
                try:
                    result_3 = html_page.find_all(class_=RESTAURANT_ADDRESS_CLASS)
                    if len(result_3) == 2:
                        adr = result_3[1].text.replace("'", "/@/")
                    else:
                        adr = result_3[0].text.replace("'", "/@/")
                except:
                    logging.error("Loi lay dia chi")
                    pass
                res.address = adr
                # lay so luot danh gia
                vie = 0
                try:
                    result_4 = html_page.find_all(class_=RESTAURANT_VIEW_CLASS)
                    vie = result_4[0].text.replace(" reviews", "").replace(" review", "")
                except:
                    logging.error("Loi lay luot danh gia")
                    pass
                res.views = vie
                # lay sao danh gia
                rev = 5
                result_5 = html_page.find_all(class_=RESTAURANT_REVIEW_1_CLASS)
                for i in result_5:
                    try:
                        a = i.find(class_=RESTAURANT_REVIEW_2_CLASS)
                        rev = float(a.div['aria-label'].replace(" star rating", ""))
                    except:
                        logging.error("Loi lay danh gia")
                        pass
                res.reviews = rev
                # lay dich vu nha hang
                result_6 = html_page.find_all(class_=RESTAURANT_SERVICE_CLASS)
                res_ser = []
                if result_6 is not None or result_6 != []:
                    for item_b in result_6:
                        item_b = item_b.find_all('span')
                        if item_b is not None or item_b != []:
                            for item_sm in item_b:
                                ser = Service()
                                ser.name = item_sm.text.replace("'", "/@/")
                                res_ser.append(ser)
                # luu lai nha hang
                insert_ser(res_ser)
                id = insert_res(res, url[1])
                insert_res_img(id, res_img)
                insert_res_ser(id, res_ser)
                # lay cac binh luan kem anh
                result_7 = html_page.find_all(class_=RESTAURANT_COMMENT_1_CLASS)
                for item in result_7[1:]:
                    temp = item.find(class_=RESTAURANT_COMMENT_IMAGE_CLASS)
                    com_img = []
                    if temp is not None or temp != []:
                        try:
                            for i in temp.find_all('img'):
                                image_c = CommentImage()
                                image_c.image = i['src']
                                com_img.append(image_c)
                        except:
                            logging.error("Loi lay anh binh luan")
                            pass
                    else:
                        pass
                    try:
                        comment = item.find(class_=RESTAURANT_COMMENT_2_CLASS).text.replace("'", "/@/")
                        cmt.comment = comment
                        cmt.restaurant_id = id
                        # luu bl, anh bl
                        id_com = insert_com(cmt)
                        insert_com_img(id_com, com_img)
                        logging.error("Loi binh luan")
                    except:
                        pass
                time.sleep(7.5)
            except:
                logging.error("khong thanh cong")
                pass
        return print("da hoan thanh")
