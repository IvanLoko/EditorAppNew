import re

import cv2
import numpy as np
from PIL import Image, ImageFile
from errors import NonePointError

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Canvas:

    def __init__(self, path=None, model=None):

        self.path = path
        self.image = self.read_image(self.path)
        self.index = self.get_index()
        self.width = 4800
        self.height = 3200
        self.kx_label = self.image.shape[1] / 1200
        self.ky_label = self.image.shape[0] / 800
        self.image = cv2.resize(self.image, (self.width, self.height))
        self.model = model

    @staticmethod
    def read_image(path: str):
        img = Image.open(path)
        return np.asarray(img)

    def get_index(self):

        with open(self.path, 'rb') as f:
            image_bytes = bytearray(f.read())
        indexes = int(re.findall('{"ID" : (\d+)}', str(image_bytes))[-1])
        del image_bytes
        return indexes

    def pins2json(self, coordinates: np.array):
        """Функция генерации json-файла пинов.

        На выходе создается json-файл вида:
        { 1 pin : [leftTop , rightBotoom],
        ...

        ...
          N pin : [leftTop , rightBotoom]
        }
        где * pin - номер пина,
        leftTop - координаты левого верхнего угла квардрата соответствующего пина
        rightBottom - координаты правого нижнего угла квардрата соответствующего пина.

        В зависимости от параметра mod, определеятся очередность нумерции пинов
        mod = {'rt', 'rb', 'lt', 'lb'}

        пин № 1 (0) будет будет присвоен в зависимости от параметра mod:

        rt -  правому верхнему
        rb - правому нижнему
        lt - левому верхнему
        lb - левому нижнему"""

        def dumping_json(centers_sorted: np.array):
            """Функция создания 'квадратов' для обозначения пинов на фото
            и последущая упаковка координат углов в json-файл"""

            width_rectangle = int(self.ky_label * 7)
            # Получаем центральную координату y для микросхемы для выравнивания меток пинов по вертикали
            mean_val = centers_sorted[:, 0].mean()

            # Получаем средние значения для координат x для левой (l_mean) части и правой (r_mean) микросхемы
            l_mean = centers_sorted[:, 0][centers_sorted[:, 0] < mean_val].mean()
            r_mean = centers_sorted[:, 0][centers_sorted[:, 0] > mean_val].mean()

            # Заменяем все значения координат x на соответствующие для "выравнивания"
            centers_sorted[:, 0][centers_sorted[:, 0] > mean_val] = r_mean
            centers_sorted[:, 0][centers_sorted[:, 0] < mean_val] = l_mean

            # Создаем координаты правого верхнего и левого нижнего пинов путем отступа 7 px.
            # В итоге получится квадрат со стороной 14 px

            rectangles = np.array([[contour[0] - width_rectangle, contour[1] - width_rectangle]
                                   for contour in centers_sorted]).astype('int16')

            left = rectangles[rectangles[:, 0] < mean_val]
            right = rectangles[rectangles[:, 0] > mean_val][::-1]

            num = 0
            if left[0, 0] > left[0, 1]:
                while num != min(len(right), len(left)):
                    if abs(left[num, 1] - right[num, 1]) > width_rectangle * 3.1:
                        if left[num, 1] > right[num, 1]:
                            left = np.insert(left, num, [left[0, 0], right[num, 1]], axis=0,)
                            num = 0
                        else:
                            right = np.insert(right, num, [right[0, 0], left[num, 1]], axis=0)
                            num = 0
                    num += 1
            else:
                while num != min(len(right), len(left)):
                    if abs(left[num, 1] - right[num, 1]) > width_rectangle * 3.1:
                        if left[num, 1] > right[num, 1]:
                            left = np.insert(left, num, [left[0, 0], right[num, 1]], axis=0, )
                            num = 0
                        else:
                            right = np.insert(right, num, [right[0, 0], left[num, 1]], axis=0)
                            num = 0
                    num += 1

            while len(right) != len(left):
                if len(right) < len(left):
                    right = np.insert(right, -1, [right[0, 0], left[len(right), 1]], axis=0)
                if len(right) > len(left):
                    left = np.insert(left, -1, [left[0, 0], right[len(left), 1]], axis=0)

            rectangles = np.concatenate([left, right[::-1]])

            num = 1
            while num < len(rectangles) - 1:
                if abs(rectangles[num, 1] - rectangles[num - 1, 1]) < width_rectangle * 3.1:
                    if rectangles[num - 1, 0] == rectangles[num, 0]:
                        row = [rectangles[num-1, 0],
                               int((rectangles[num, 1] + rectangles[num - 1, 1]) / 2)]
                        rectangles = np.delete(rectangles, (num - 1, num), axis=0)
                        rectangles = np.insert(rectangles, num-1, row, axis=0)
                num += 1

            return rectangles

        # Coordinates: 1 - horizontal min, 2 - vertical min, 3 - horizontal max, 4 - vertical max
        y1, x1, y2, x2 = coordinates

        crop_img = self.image[min(x1, x2):max(x1, x2), min(y1, y2):max(y1, y2)]
        #   Сохраняем исходные размерности изображения
        width, height = crop_img.shape[:2]

        #   Так как нейронная сеть работает с изображениями 256х256, изменяем размерность изображения
        crop_img = cv2.resize(crop_img, (256, 256)) / 255

        #   Определяем коэффициенты для корректировки итоговых координат пинов
        kx, ky = width / 256, height / 256

        #   Сегмнтируем изобраэжение
        det = self.model.predict(crop_img[None, ...])[0, ...][:, :, 1]

        #   Устанавливаем пороги при которых будем считать что пиксель является пином, а не фоном
        det = np.where(det > 0.018, 255, 0)

        #   Находим контуры выделенных пинов
        contours, _ = cv2.findContours(
            det.copy(),
            cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)

        #   Формируем центры найденных областей, центром будем считать мат. ожидание кординат контура
        centers = list()
        for cnt in contours[0:-1:2]:
            if cv2.contourArea(cnt) > 200 and (cnt.mean(axis=0)[0][0] > 175 or cnt.mean(axis=0)[0][0] < 75):
                centers.append(cnt.mean(axis=0))

        #   Масштабируем координаты
        centers = np.array(centers).reshape(-1, 2)

        if not centers.any():
            raise NonePointError(f'centers should be non empty list: {type(centers)}')

        centers[:, 0] = ((centers[:, 0] * ky) + min(y1, y2)).astype('int32')
        centers[:, 1] = ((centers[:, 1] * kx) + min(x1, x2)).astype('int32')

        # Мод = 'rb'
        if x1 > x2 and y1 > y2:
            cen_sorted = sorted(
                centers[centers[:, 0] > centers[:, 0].mean()], key=lambda x: x[1]
            ) + sorted(
                centers[centers[:, 0] < centers[:, 0].mean()], key=lambda x: x[1], reverse=True
            )
            return dumping_json(centers_sorted=np.array(cen_sorted))

        #   Мод = 'lt'
        if x1 < x2 and y1 < y2:
            cen_sorted = sorted(
                centers[centers[:, 0] < centers[:, 0].mean()], key=lambda x: x[1]
            ) + sorted(
                centers[centers[:, 0] > centers[:, 0].mean()], key=lambda x: x[1], reverse=True
            )
            if len(cen_sorted) == 0:
                raise NonePointError(f'cen_sorted should be non empty list, but {len(cen_sorted)}')

            return dumping_json(centers_sorted=np.array(cen_sorted))
