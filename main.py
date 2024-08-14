import cairo
import random
from io import BytesIO
from PIL import Image
from src import shape as sh


height, width = 250, 250
colors = [(181, 168, 250), (204, 196, 252), (95, 237, 223), (28, 94, 87), (32, 0, 82), (13, 0, 33), (74, 0, 43),
          (96, 0, 78), (38, 0, 31), (158, 245, 237), (199, 105, 158), (204, 196, 252), (128, 51, 112), (248, 237, 231),
          (191, 247, 242), (217, 156, 191)]

bg = (.514, .431, .976)

min_h, max_h = 5, 15
min_w, max_w = 5, 15
min_gap, max_gap = 1, 3


def draw_rectangle_fill(cr, x, y, r, g, b):
    cr.set_source_rgb(r, g, b)
    cr.rectangle(x, y, 1, 1)
    cr.fill()


def draw_background(cr, r, g, b, w, h):
    cr.set_source_rgb(r, g, b)
    cr.rectangle(0, 0, w, h)
    cr.fill()


def draw_cells(cr, dp):
    for i in range(width):
        for j in range(height):
            draw_rectangle_fill(cr, i, j, dp[i][j][0], dp[i][j][1], dp[i][j][2])


def draw_rectangle(cr, x, y, r, g, b, w, h):
    cr.set_source_rgb(r, g, b)
    cr.rectangle(x, y, w, h)
    cr.fill_preserve()  # Preserve the path for stroking later

    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(1)
    cr.stroke()  # Stroke the outline of the rectangle


def draw_border(cr, size, r, g, b, w, h):
    cr.set_source_rgb(r, g, b)
    cr.rectangle(0, 0, size, h)
    cr.rectangle(0, 0, w, size)
    cr.rectangle(0, h - size, w, size)
    cr.rectangle(w - size, 0, size, h)
    cr.fill()


def mark_area(dp, i, j, w, h, r, g, b):
    for x in range(i, i + w):
        for y in range(j, j + h):
            dp[x][y] = (r, g, b)
    return dp


def is_rectangle_in_marked_area(dp, i, j, w, h):
    # Iterate over all pixels in the rectangle defined by (i, j, w, h)
    for x in range(i, i + w):
        for y in range(j, j + h):
            # Check if the pixel is marked as True in dp
            if dp[x][y] != bg:
                return True  # Overlap found
    return False  # No overlap found


def next_gen(dp, angle):
    neighbor_offsets = [
        (-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
        (0, -1), (0, 1),  # Left, Right
        (1, -1), (1, 0), (1, 1)  # Bottom-left, Bottom, Bottom-right
    ]

    new_dp = [[bg] * height for _ in range(width)]
    rot_polygon = sh.rotate_polygon(angle, sh.polygon)

    for i in range(width):
        for j in range(height):
            count = 0
            color_set = []
            for offset in neighbor_offsets:
                ni, nj = i + offset[0], j + offset[1]
                if 0 <= ni < width and 0 <= nj < height:

                    if dp[ni][nj] != bg:
                        count += 1
                        color_set.append(dp[ni][nj])  # Collect neighbor's color

            if sh.is_point_in_shape(i, j, rot_polygon):
                if dp[i][j] != bg:
                    if 2 < count:
                        new_dp[i][j] = random.choice(color_set)
                else:
                    if count > 2 and color_set:
                        new_dp[i][j] = random.choice(color_set)

    return new_dp


def main(number: int):

    collected_frames = []

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(ims)

    dp = [[bg] * height for _ in range(width)]
    draw_rectangle(cr, 0, 0, .514, .431, .976, width, height)

    for i in range(4, width - 5):
        for j in range(4, height - 5):
            if dp[i][j] == bg:
                w = random.randint(min_w, max_w)
                h = random.randint(min_h, max_h)
                gap_x = random.randint(min_gap, max_gap)
                gap_y = random.randint(min_gap, max_gap)

                while h + j > height or any(dp[i][y] != bg for y in range(j, j + h)):
                    h -= 1

                while w + i > width or any(dp[x][j] != bg for x in range(i, i + w)):
                    w -= 1

                if (w > min_w and h > min_h and not is_rectangle_in_marked_area(dp, i, j, w, h)
                        and i + w < width - min_gap and j + h < height - min_gap):

                    if (sh.is_point_in_shape(i + gap_x, j + gap_y) and
                            sh.is_point_in_shape(i + w - gap_x, j + h - gap_y)):

                        color = random.choice(colors)
                        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
                        draw_rectangle(cr, i + gap_x, j + gap_y, r, g, b, w - gap_x, h - gap_y)
                        dp = mark_area(dp, i + gap_x, j + gap_y, w - gap_x, h - gap_y, r, g, b)

    for i in range(number):
        print(i + 1)

        dp = next_gen(dp, i)
        draw_background(cr, bg[0], bg[1], bg[2], width, height)  # Clear background
        draw_cells(cr, dp)

        buf = BytesIO()
        ims.write_to_png(buf)
        buf.seek(0)
        frame_image = Image.open(buf)
        collected_frames.append(frame_image)

    collected_frames += collected_frames[::-1]
    collected_frames[0].save(f'examples/{random.randint(1, 10000)}-{number}gen-GoL.gif', format='GIF', save_all=True,
                             append_images=collected_frames,
                             optimize=False, duration=33, loop=0)


main(int(input('Generations: ')))
