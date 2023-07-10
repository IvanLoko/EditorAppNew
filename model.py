from keras import Input, Model
from keras.layers import Conv2D, MaxPool2D, Conv2DTranspose, concatenate


def build_model():
    x = Input((256, 256, 3))

    out = Conv2D(64, (3, 3), padding='same', activation='relu')(x)
    out1 = Conv2D(64, (3, 3), padding='same', activation='relu')(out)
    out = MaxPool2D((2, 2))(out1)

    out = Conv2D(128, (3, 3), padding='same', activation='relu')(out)
    out2 = Conv2D(128, (3, 3), padding='same', activation='relu')(out)
    out = MaxPool2D((2, 2))(out2)

    out = Conv2D(256, (3, 3), padding='same', activation='relu')(out)
    out3 = Conv2D(256, (3, 3), padding='same', activation='relu')(out)
    out = MaxPool2D((2, 2))(out3)

    out = Conv2D(512, (3, 3), padding='same', activation='relu')(out)
    out4 = Conv2D(512, (3, 3), padding='same', activation='relu')(out)
    out = MaxPool2D((2, 2))(out4)

    out = Conv2D(1024, (3, 3), padding='same', activation='relu')(out)
    out = Conv2D(1024, (3, 3), padding='same', activation='relu')(out)

    out = Conv2DTranspose(512, (3, 3), strides=(2, 2), padding='same', activation='relu')(out)
    out = concatenate([out4, out], axis=3)

    out = Conv2D(512, (3, 3), padding='same', activation='relu')(out)
    out = Conv2D(512, (3, 3), padding='same', activation='relu')(out)

    out = Conv2DTranspose(256, (3, 3), strides=(2, 2), padding='same', activation='relu')(out)
    out = concatenate([out3, out], axis=3)

    out = Conv2D(256, (3, 3), padding='same', activation='relu')(out)
    out = Conv2D(256, (3, 3), padding='same', activation='relu')(out)

    out = Conv2DTranspose(128, (3, 3), strides=(2, 2), padding='same', activation='relu')(out)
    out = concatenate([out2, out], axis=3)

    out = Conv2D(128, (3, 3), padding='same', activation='relu')(out)
    out = Conv2D(128, (3, 3), padding='same', activation='relu')(out)

    out = Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same', activation='relu')(out)
    out = concatenate([out1, out], axis=3)

    out = Conv2D(64, (3, 3), padding='same', activation='relu')(out)
    out = Conv2D(64, (3, 3), padding='same', activation='relu')(out)

    # Выбираем softmax, так как формально класса 2 - пины и фон
    out = Conv2D(2, (3, 3), padding='same', activation='softmax')(out)

    return Model(inputs=x, outputs=out)
