from cStringIO import StringIO
import Image

THUMB_SIZE = 120, 120


def load_square_resized(filename):
    """This loads an image file, resize it to a quare thumbnail and give
    a Stream to it back.

    :type filename: str
    :param filename: The filename to load/resize.
    :rtype: StringIO
    :return: The Stream of the image
    """
    io = StringIO()
    _resize_image_square(filename, io)
    io.seek(0)
    return io


def _resize_image_square(path, output_handle):
    """This resizes an image to a square thumbnail.

    :param path: The path of the original image.
    :param output_handle: A I/O handle to write the result to.
    :return: Returns the given output handle with the stream written to.
    """
    img = Image.open(path)
    width, height = img.size

    if width > height:
        delta = width - height
        left = int(delta / 2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta / 2)
        right = width
        lower = width + upper

    img = img.crop((left, upper, right, lower))
    img.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    img.save(output_handle, 'JPEG', quality=70)
    return output_handle