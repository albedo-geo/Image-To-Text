import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
from pathlib import Path
import time
from tqdm import tqdm


def get_alphabet(choice) -> str:
    """get the alphabet used to print on the output image"""
    if choice == 'uppercase':
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif choice == 'lowercase':
        return 'abcdefghijklmnopqrstuvwxyz'
    elif choice == 'alphabet':
        return get_alphabet('uppercase') + get_alphabet('lowercase')
    elif choice == 'number':
        return '0123456789'
    elif choice == 'alphanumeric':
        return get_alphabet('alphabet') + get_alphabet('number')
    elif choice == 'symbol':
        return r'~!@#$%^&*()-_=+[]{}\|;:,<.>/?"'
    elif choice == 'random':
        return get_alphabet('alphanumeric') + get_alphabet('symbol')


def get_background(choice: str, origin, width, height) -> Image.Image:
    """generate a canvas to print"""
    if choice == 'transparent':
        # 4-channel
        return Image.fromarray(np.uint8(np.zeros((height, width, 4))))
    elif choice == 'black':
        return Image.fromarray(np.uint8(np.zeros((height, width, 3))))
    elif choice == 'white':
        return Image.fromarray(np.uint8(np.ones((height, width, 3)) * 255))
    elif choice == 'mean':
        mean = np.mean(np.array(origin)[:])
        return Image.fromarray(np.uint8(np.ones((height, width, 3)) * mean))
    elif choice.startswith('origin'):
        opacity = float(choice[-1]) / 10
        canvas = origin.resize((width, height), Image.BICUBIC).filter(
            ImageFilter.GaussianBlur(25)
        )
        canvas = np.array(canvas)
        canvas = np.uint8(canvas[:, :, 0:3] * opacity)
        return Image.fromarray(canvas)


def color(
    input: str,
    output: str = None,
    rows: int = 100,
    alphabet='uppercase',
    background='origin7',
    out_height: int = None,
    scale: float = None,
):
    """output colorful text picture"""
    input_path = Path(input)
    # the original image
    origin = Image.open(input_path)
    width, height = origin.size
    print(f'input size: {origin.size}')
    # text amount of the output image
    text_rows = rows
    text_cols = round(width / (height / text_rows) * 1.25)  # char height-width ratio
    origin_ref_np = cv2.resize(
        np.array(origin), (text_cols, text_rows), interpolation=cv2.INTER_AREA
    )
    origin_ref = Image.fromarray(origin_ref_np)
    # font properties
    fontsize = 17
    font = ImageFont.truetype('courbd.ttf', fontsize)
    char_width = 8.88
    char_height = 11
    # output size depend on the rows and cols
    canvas_height = round(text_rows * char_height)
    canvas_width = round(text_cols * char_width)
    # a canvas used to draw texts on it
    canvas = get_background(background, origin, canvas_width, canvas_height)
    print(f'canvas size: {canvas.size}')
    # start drawing
    since = time.time()
    print(f'Start transforming {input_path.name}')
    draw = ImageDraw.Draw(canvas)
    charlist = get_alphabet(alphabet)
    length = len(charlist)

    for i in tqdm(range(text_cols)):
        for j in range(text_rows):
            x = round(char_width * i)
            y = round(char_height * j - 4)
            char = charlist[random.randint(0, length - 1)]
            color = origin_ref.getpixel((i, j))
            draw.text((x, y), char, fill=color, font=font)
    # resize the reproduct if necessary
    if out_height:  # height goes first
        canvas_height = out_height
        canvas_width = round(width * canvas_height / height)
        canvas = canvas.resize((canvas_width, canvas_height), Image.BICUBIC)
    elif scale:
        canvas_width = round(width * scale)
        canvas_height = round(height * scale)
        canvas = canvas.resize((canvas_width, canvas_height), Image.BICUBIC)
    # output filename
    if output:
        output_path = Path(output)
    else:
        output_path = input_path.with_name(
            f'{input_path.stem}_{canvas_width}x{canvas_height}_D{text_rows}_{background}.png'
        )
    canvas.save(output_path)

    print(f'Transformation completed. Saved as {output_path.name}.')
    print(f'Output image size: {canvas_width}x{canvas_height}')
    print(f'Text density: {text_cols}x{text_rows}')
    print(f'Elapsed time: {time.time() - since:.4} second(s)')
