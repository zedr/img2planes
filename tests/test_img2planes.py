import os
from img2planes import PlaneImage, padded

_dirname = os.path.dirname(__file__)
test_png_path = os.path.join(_dirname, 'fixtures', 'test.png')
test2_png_path = os.path.join(_dirname, 'fixtures', 'test2.png')
test32_png_path = os.path.join(_dirname, 'fixtures', 'test32.png')


def test_size():
    img = PlaneImage(test_png_path)
    assert img.original_width == 24
    assert img.width == 32
    assert img.height == 10


def test_n_planes():
    img = PlaneImage(test_png_path)
    assert len(img.planes) == 3


def test_colors():
    img = PlaneImage(test_png_path)
    assert img.palette == (
        (255, 255, 255),
        (0, 0, 0),
        (0, 28, 255),
        (255, 0, 0),
        (0, 255, 66),
        (255, 250, 0)
    )


def test_n_pixels():
    img = PlaneImage(test_png_path)
    assert len(list(img.planes[0].as_pixels())) == 320
    assert len(list(img.planes[1].as_pixels())) == 320
    assert len(list(img.planes[2].as_pixels())) == 320


def test_padding():
    data = [1, 1, 1, 0, 0, 0]
    assert padded(data, 2)[0] == [
        1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]


def test_c_colors_6():
    img = PlaneImage(test_png_path)
    assert img.as_c_colors() == "UWORD colordata[] = { 0xfff, 0x000, 0x01f, 0xf00, 0x0f4, 0xff0 };"


def test_c_colors_8():
    img = PlaneImage(test2_png_path)
    assert img.as_c_colors() == "UWORD colordata[] = { 0xa20, 0x700, 0x000, 0xf00, 0xf75, 0x333, 0x999, 0xfff };"


def test_c_colors_32():
    img = PlaneImage(test_png_path)
    #for c1, c2 in zip(img.palette, img.reduced_palette):
    #    print(c1, c2)
    assert False
