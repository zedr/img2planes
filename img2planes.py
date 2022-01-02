#!/usr/bin/env python3

import io
import sys
import argparse
from ast import literal_eval
from collections import defaultdict, namedtuple

from PIL import Image, ImageCms


CropBox = namedtuple('CropBox', 'x y width height')


class Plane:
    def __init__(self, plane_data, width):
        self._original_width = width
        self._data, padding = padded(plane_data, width)
        self._width = width + padding
        self._words = []

    def comma_sep_words(self):
        return ", ".join(str(word) for word in self.as_words())

    def as_words(self):
        if self._words:
            return self._words
        else:
            self._words = list(worded(self._data))
            return self._words

    def as_dotted_image(self):
        for idx, bit in enumerate(self._data, start=1):
            yield '#' if bit else ' '
            if idx % self._width == 0:
                yield '|\n'

    def as_pixels(self):
        for px in self._data:
            yield px


def bin_(num):
    return bin(num)[2:]


def list_to_word(li):
    return hex(literal_eval('0b' + ''.join(str(el) for el in li)))


def image_to_array(image):
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            yield pixels[x, y]


def create_palette(pixels):
    palette = defaultdict(int)
    for px in pixels:
        palette[px] += 1

    for c, col in sorted(((c, k) for k, c in palette.items()), reverse=True):
        yield col


def create_chunky_plane(sequence, palette):
    filling = len(bin_(len(palette) - 1))
    for px in sequence:
        idx = palette.index(px)
        yield list(bin_(idx).zfill(filling))


def create_bitplanes(chunky_plane):
    try:
        n_planes, = {len(el) for el in chunky_plane}
    except ValueError:
        raise ValueError(
            'Invalid chunky plane. Plane cells have variable length.'
        )

    for idx in range(n_planes):
        plane = []
        for px in chunky_plane:
            plane.append(int(px.pop()))
        yield plane


def padded(data, width, size=16):
    new_data = []
    offset = size - divmod(width, size)[1]
    padding = [] if offset == 16 else [0] * offset
    while data:
        row, data = data[:width], data[width:]
        assert len(row) == width
        new_data.extend(row + padding)
    return (new_data, len(padding))


def worded(plane):
    assert len(plane) % 16 == 0
    while plane:
        word, plane = plane[:16], plane[16:]
        yield list_to_word(word)


def cropped(arr, orig_width, x, y, width, height):
    _arr = arr[:(orig_width * (y + (height - 1))) + (x + width)]
    _arr = _arr[(orig_width * y) + x:]
    new_arr = []
    rest = orig_width - width
    while _arr:
        new_arr += _arr[:width]
        _arr = _arr[width + rest:]

    return new_arr


class PlaneImage:
    def __init__(self, name, crop=None):
        img = self._img = Image.open(name).convert('RGB')
        icc = img.info.get('icc_profile', '')
        self._height = CropBox(*crop).height if crop else img.height
        if icc:
            io_handle = io.BytesIO(icc)
            src_profile = ImageCms.ImageCmsProfile(io_handle)
            dst_profile = ImageCms.createProfile('sRGB')
            img = ImageCms.profileToProfile(img, src_profile, dst_profile)
        arr = list(image_to_array(img))
        self._palette = tuple(create_palette(arr))
        chunky = list(create_chunky_plane(arr, self._palette))
        self._planes = tuple(
            Plane(plane, CropBox(*crop).width if crop else img.width)
            for plane in create_bitplanes(
                cropped(chunky, img.width, *crop) if crop else chunky
            )
        )

    @property
    def planes(self):
        return self._planes

    @property
    def width(self):
        return self._planes[0]._width

    @property
    def height(self):
        return self._height

    @property
    def original_width(self):
        return self._planes[0]._original_width

    @property
    def palette(self):
        return self._palette

    @property
    def reduced_palette(self):
        return tuple(
            tuple(n >> 4 for n in col) for col in self._palette
        )

    @property
    def n_words(self):
        return ((self.width * self.height) / 16) * len(self.planes)

    def as_c_array(self, name="image_data"):
        return "UWORD __chip %s[] = { %s };" % (
            name,
            ', '.join(plane.comma_sep_words() for plane in self.planes)
        )

    def as_c_colors(self, name="colordata"):
        cols = [[hex(c)[2] for c in col] for col in self.reduced_palette]

        return "UWORD %s[] = { %s };" % (
            name,
            ", ".join('0x' + ''.join(col) for col in cols)
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('IMAGE_NAME')
    parser.add_argument(
        '--name',
        '-n',
        dest='name',
        default='image_data',
        help='Name of the data structure instance (for the "array" format)'
    )
    parser.add_argument(
        '--format',
        '-f',
        dest='format',
        default='bitplanes',
        help='Output format. Choose from: bitplanes, array, image'
    )
    parser.add_argument(
        '--crop',
        '-c',
        dest='crop',
        default=None,
        help='Crop to rectangle. Format: x,y,width,height'
    )
    parser.add_argument(
        '--no-colors',
        '-C',
        dest='no_colors',
        default=False,
        action='store_true',
        help='Do not output the color data (for the "array" format)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        dest='verbose',
        default='False',
        action='store_true'
    )
    args = parser.parse_args()
    if args.crop:
        crop_box = tuple(int(num) for num in args.crop.split(','))
    else:
        crop_box = None
    img = PlaneImage(args.IMAGE_NAME, crop=crop_box)
    if args.format == 'bitplanes':
        for idx, plane in enumerate(img.planes, 1):
            print('%s.' % idx)
            print(''.join(plane.as_dotted_image()))
    elif args.format == 'array':
        print(img.as_c_array(name=args.name))
        if not args.no_colors:
            print(img.as_c_colors(name=args.name + '_colors'))
    else:
        try:
            img._img.save(sys.stdout, args.format)
        except KeyError:
            print(f'ERROR: unsupported format: {args.format}', file=sys.stderr)
            sys.exit(1)

    if args.verbose:
        n_planes = len(img.planes)
        sys.stderr.write('width: %s\n' % str(img.original_width))
        sys.stderr.write('padded width: %s\n' % str(img.width))
        sys.stderr.write('height: %s\n' % str(img.height))
        sys.stderr.write('planes: %s\n' % n_planes)
        sys.stderr.write('words: %s\n' % int(img.n_words))
        sys.stderr.write('colors: %s\n' % len(img.palette))


if __name__ == "__main__":
    main()
