import math
import typing


def draw_rectangle(
    ctx,
    x: int,
    y: int,
    width: int,
    height: int,
    border_radius: int,
    border_size: int,
    color: list[int],
    border_color: list[int] | None,
) -> None:
    ctx.set_source_rgba(color[0] / 255, color[1] / 255, color[2] / 255, color[3])
    if border_radius > 0:
        corner_radius = border_radius

        radius = corner_radius
        degrees = math.pi / 180.0

        ctx.new_sub_path()
        ctx.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
        ctx.arc(
            x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees
        )
        ctx.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        ctx.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        ctx.close_path()

        ctx.fill_preserve()
        if border_size != 0:
            ctx.set_source_rgba(
                border_color[0] / 255,
                border_color[1] / 255,
                border_color[2] / 255,
                border_color[3],
            )
            ctx.set_line_width(border_size)
            ctx.stroke()
    else:
        ctx.rectangle(x, y, width, height)
        if border_size != 0:
            ctx.fill_preserve()
            ctx.set_source_rgba(
                border_color[0] / 255,
                border_color[1] / 255,
                border_color[2] / 255,
                border_color[3],
            )
            ctx.set_line_width(border_size)
            ctx.stroke()
        else:
            ctx.fill()
    return None
