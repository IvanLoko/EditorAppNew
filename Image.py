import cv2
import matplotlib.pyplot as plt
import numpy as np


class Image:

    def __init__(self, path=None, model=None):

        self.path = path
        self.image = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        self.width = 4800
        self.height = 3200
        self.image = cv2.resize(self.image, (self.width, self.height))
        self.model = model


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

        def dumping_json(cen_sorted: np.array):
            """Функция создания 'квадратов' для обозначения пинов на фото
            и последущая упаковка координат углов в json-файл"""

            # Получаем центральную координату y для микросхемы для выравнивания меток пинов по вертикали
            mean_val = abs(y1 - y2) / 2 + min(y1, y2)

            # Получаем средние значения для координат y для левой (l_mean) части и правой (r_mean) микросхемы
            l_mean = (cen_sorted[cen_sorted[:, 0] < mean_val][:, 0]).mean()
            r_mean = (cen_sorted[cen_sorted[:, 0] > mean_val][:, 0]).mean()

            # Заменяем все значения координат y на соответствующие для "выравнивания"
            cen_sorted[:, 0][cen_sorted[:, 0] > mean_val] = int(r_mean)
            cen_sorted[:, 0][cen_sorted[:, 0] < mean_val] = int(l_mean)

            # Создаем координаты правого верхнего и левого нижнего пинов путем отступа 5 px.
            # В итоге получится квадрат со стороной 10 px

            rectangles = [[cnt[0] - 7, cnt[1] - 7] for cnt in cen_sorted]
            return rectangles
        # Coordinates: 1 - horizontal min, 2 - vertical min, 3 - horizontal max, 4 - vertical max
        y1, x1, y2, x2 = coordinates

        crop_img = self.image[min(x1, x2):max(x1, x2), min(y1, y2):max(y1, y2)]
        # if x1 > x2 and y1 > y2:
        #     mod = 'lb'  # lb
        #
        #     mod = 'lt'  # lt
        # if x1 > x2 and y1 < y2:
        #     mod = 'rb'  # rb

        #   Сохраняем исходные размерности изображения
        width, height = crop_img.shape[:2]

        #   Так как нейронная сеть работает с изображениями 256х256, изменяем размерность изображения
        crop_img = cv2.resize(crop_img, (256, 256)) / 255

        #   Определяем коэффициенты для корректировки итоговых координат пинов
        kx, ky = width / 256, height / 256

        #   Сегмнтируем изобраэжение
        det = self.model.predict(crop_img[None, ...])[0, ...][:, :, 1]

        #   Устанавливаем пороги при которых будем считать что пиксель является пином, а не вотно
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
        centers[:, 0] = (centers[:, 0] * ky).astype('int32') + min(y1, y2)
        centers[:, 1] = (centers[:, 1] * kx).astype('int32') + min(x1, x2)

          # Мод = 'rb'
        if x1 > x2 and y1 > y2:
            cen_sorted = sorted(
                centers[centers[:, 0] > width + min(y1, y2)], key=lambda x: x[1], reverse=True
            ) + sorted(
                centers[centers[:, 0] < width + min(y1, y2)], key=lambda x: x[1],
            )
            return dumping_json(cen_sorted=np.array(cen_sorted))

        #   Мод = 'lt'
        if x1 < x2 and y1 < y2:
            cen_sorted = sorted(
                centers[centers[:, 0] < width + min(y1, y2)], key=lambda x: x[1]
            ) + sorted(
                centers[centers[:, 0] > width + min(y1, y2)], key=lambda x: x[1], reverse=True
            )
            return dumping_json(cen_sorted=np.array(cen_sorted))

