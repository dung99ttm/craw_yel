import logging
from sqlalchemy import create_engine
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base


""" Tao doi tuong mau """
Base = declarative_base()
""" Ket noi CSDL """
engine = create_engine("mysql://root:Cochacdaykhongconlaanh@localhost:3306/craw_yelp", echo=True)
session = Session(engine)
session.connection()


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8_vietnamese_ci'), nullable=False, unique=True)


class CategoryRestaurant(Base):
    __tablename__ = 'category_restaurants'

    id = Column(Integer, primary_key=True)
    category_id = Column(ForeignKey('categories.id'), index=True, nullable=False)
    restaurant_id = Column(ForeignKey('restaurants.id'), index=True, nullable=False)

    category = relationship('Category', primaryjoin='CategoryRestaurant.category_id == Category.id',
                            backref='category_restaurants')
    restaurant = relationship('Restaurant', primaryjoin='CategoryRestaurant.restaurant_id == Restaurant.id',
                              backref='category_restaurants')


class CommentImage(Base):
    __tablename__ = 'comment_images'

    id = Column(Integer, primary_key=True)
    image = Column(String(255, 'utf8_vietnamese_ci'), nullable=False)
    comment_id = Column(ForeignKey('comments.id'), index=True, nullable=False)

    comment = relationship('Comment', primaryjoin='CommentImage.comment_id == Comment.id', backref='comment_images')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    comment = Column(String(20000, 'utf8_vietnamese_ci'), nullable=False)
    restaurant_id = Column(ForeignKey('restaurants.id'), index=True)

    restaurant = relationship('Restaurant', primaryjoin='Comment.restaurant_id == Restaurant.id', backref='comments')


class RestaurantImage(Base):
    __tablename__ = 'restaurant_images'

    id = Column(Integer, primary_key=True)
    image = Column(String(255, 'utf8_vietnamese_ci'), nullable=False)
    restaurant_id = Column(ForeignKey('restaurants.id'), index=True, nullable=False)

    restaurant = relationship('Restaurant', primaryjoin='RestaurantImage.restaurant_id == Restaurant.id',
                              backref='restaurant_images')


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8_vietnamese_ci'), nullable=False, unique=True)
    address = Column(String(255, 'utf8_vietnamese_ci'))
    reviews = Column(Float)
    views = Column(Integer)


class ServiceRestaurant(Base):
    __tablename__ = 'service_restaurants'

    id = Column(Integer, primary_key=True)
    service_id = Column(ForeignKey('services.id'), index=True, nullable=False)
    restaurant_id = Column(ForeignKey('restaurants.id'), index=True, nullable=False)

    restaurant = relationship('Restaurant', primaryjoin='ServiceRestaurant.restaurant_id == Restaurant.id',
                              backref='service_restaurants')
    service = relationship('Service', primaryjoin='ServiceRestaurant.service_id == Service.id',
                           backref='service_restaurants')


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8_vietnamese_ci'), nullable=False, unique=True)


def insert_res(res, cate):
    """
    Them chi tiet thong tin nha hang, loai nha hang vào CSDL

    :param res: Thong tin chi tiet nha hang
    :param cate: id Loai nha hang
    :return: id nha hang
    """

    session.add(res)
    session.commit()

    """ luu category cua nha hang """
    session.add(CategoryRestaurant(restaurant_id=res.id, category_id=cate))
    session.commit()
    return res.id


def insert_ser(ser):
    """
    Them cac dich vu tu trang web vao CSDL

    :param ser: danh sach cac dich vu
    :return: True
    """

    if ser is not None or ser != []:
        for i in ser:
            try:
                session.add(i)
                session.commit()
            except Exception as e:
                session.close()
                logging.error(str(e))
                pass
    session.close()
    return True


def insert_res_img(id, res_img):
    """
    Them cac anh tieu bieu cua tung nha hang vao CSDL

    :param id: id nha hang
    :param res_img: danh sach doi tuong anh cua nha hang
    :return: True
    """

    if res_img is not None or res_img != []:
        for i in res_img:
            i.restaurant_id = id
            session.add(i)
            session.commit()
    return True


def insert_res_ser(id, res_ser):
    """
    Them cac dich vu cua tung nha hang vao CSDL

    :param id: id nha hang
    :param res_ser: danh sach doi tuong dich vu cua nha hang
    :return:True
    """

    if res_ser is not None or res_ser != []:
        for i in res_ser:
            print(i.name)
            a = session.query(Service).filter_by(name=i.name).first()
            session.add(ServiceRestaurant(restaurant_id=id, service_id=a.id))
            session.commit()
    return True


def insert_com(cmt):
    """
    Them binh luan len CSDL

    :param cmt: doi tuong binh luan
    :return:id binh luan
    """

    session.add(cmt)
    session.commit()
    return cmt.id


def insert_com_img(id_com, com_img):
    """
    Them cac anh cua tung binh luan vao CSDL

    :param id_com: id binh luan
    :param com_img: danh sach doi tuong anh cua binh luan
    :return:True
    """

    if com_img is not None or com_img != []:
        for i in com_img:
            i.comment_id = id_com
            session.add(i)
            session.commit()

    return True


def get_categories():
    """
    Lay ra danh sach cac loai nha hang
    
    :return: tra lai danh sach cac doi tuong loai nha hang
    """""
    result = session.query(Category).all()
    return result
