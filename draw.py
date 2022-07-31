import typing

def draw_border(
    ctx,
    x: int,
    y: int,
    width: int,
    height: int,
    radius: int,
    border_width: int,
    border_color: list[int],
) -> None:
    if border_width != 0:
        r = border_color[0] / 255
        g = border_color[1] / 255
        b = border_color[2] / 255
        a = border_color[3]

        if radius > 0:
            degrees = 0.017453292519943295 # pi/180
            ctx.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
            ctx.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
            ctx.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
            ctx.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
            ctx.close_path()
        else:
            ctx.rectangle(x, y, width, height)

        ctx.set_source_rgba(r, g, b, a)
        ctx.set_line_width(border_width)
        ctx.stroke()

    return None
