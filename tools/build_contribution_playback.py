"""Render the public GitHub contribution calendar as Atomic Signal artwork."""

import argparse
from bisect import bisect_right
from datetime import date, timedelta
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont


CALENDAR_URL = 'https://github.com/users/JayacharanR/contributions'
WIDTH, HEIGHT = 928, 180
PITCH = 15
CELL = 11
GRID_TOP = 42
BACKGROUND = '#0b1011'
PANEL = '#131a1b'
BORDER = '#35443b'
TEXT = '#edf0e6'
MUTED = '#a8b5aa'
SIGNAL = (231, 255, 88)
LEVELS = ('#222c29', '#46542c', '#6b8033', '#9aad42', '#cce557')


class ContributionTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag != 'td':
            return
        cell = dict(attrs)
        if 'ContributionCalendar-day' in cell.get('class', '').split():
            if 'data-date' in cell and 'data-level' in cell:
                self.cells.append((date.fromisoformat(cell['data-date']), int(cell['data-level'])))


def read_calendar(snapshot):
    if snapshot:
        data = json.loads(snapshot.read_text())
        first = date.fromisoformat(data['first'])
        cells = [(first + timedelta(days=i), int(level)) for i, level in enumerate(data['levels'])]
        if not cells or cells[-1][0].isoformat() != data['last']:
            raise ValueError('Snapshot date range and activity levels disagree.')
    else:
        request = Request(CALENDAR_URL, headers={'User-Agent': 'JayacharanR profile calendar renderer'})
        with urlopen(request, timeout=25) as response:
            html = response.read(2_000_001)
        if len(html) > 2_000_000:
            raise ValueError('Unexpectedly large calendar response.')
        parser = ContributionTable()
        parser.feed(html.decode('utf-8'))
        cells = sorted(parser.cells)
    if not 360 <= len(cells) <= 371:
        raise ValueError(f'Expected one year of calendar days, received {len(cells)}.')
    first = cells[0][0]
    for i, (day, level) in enumerate(cells):
        if day != first + timedelta(days=i) or not 0 <= level < len(LEVELS):
            raise ValueError('Calendar dates or activity levels are invalid.')
    return cells


def render(cells, output):
    first, last = cells[0][0], cells[-1][0]
    leading = (first.weekday() + 1) % 7
    weeks = (leading + len(cells) + 6) // 7
    grid_left = (WIDTH - (weeks - 1) * PITCH - CELL) // 2
    base = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(base)
    draw.polygon([(1,1),(914,1),(926,13),(926,178),(13,178),(1,166)], fill=PANEL, outline=BORDER)
    draw.rectangle((2,2,6,33), fill=SIGNAL)
    title_font = ImageFont.load_default(size=17)
    label_font = ImageFont.load_default(size=12)
    draw.text((24, 13), 'Contribution Activity', fill=TEXT, font=title_font)
    draw.text((grid_left, 155), f'{first:%b %d, %Y} to {last:%b %d, %Y}', fill=MUTED, font=label_font)
    draw.text((741, 161), 'Less', fill=MUTED, font=label_font, anchor='rm')
    for i, color in enumerate(LEVELS):
        x = 752 + i * 15
        draw.rounded_rectangle((x,156,x+9,165), radius=2, fill=color)
    draw.text((831, 161), 'More', fill=MUTED, font=label_font, anchor='lm')

    grid = []
    active = []
    for index, (_, level) in enumerate(cells, leading):
        week, day = divmod(index, 7)
        x, y = grid_left + week * PITCH, GRID_TOP + day * PITCH
        grid.append((week, x, y, level))
        if level:
            active.append((week + (day + .5) / 7, x + CELL/2, y + CELL/2))
    times = [event[0] for event in active]

    def position(cursor):
        i = bisect_right(times, cursor)
        if not i:
            return None
        t0, x0, y0 = active[i-1]
        if i == len(active):
            return x0, y0
        t1, x1, y1 = active[i]
        start = max(t0, int(t1))
        phase = max(0, (cursor - start) / (t1 - start))
        return x0 + (x1 - x0) * phase, y0 + (y1 - y0) * phase

    def frame(cursor, animated=True):
        image = base.copy()
        ink = ImageDraw.Draw(image, 'RGBA')
        shown = min(weeks, int(cursor) + 1)
        for week, x, y, level in grid:
            color = LEVELS[level] if week < shown else LEVELS[0]
            ink.rounded_rectangle((x,y,x+CELL-1,y+CELL-1), radius=2, fill=color)
        caption = f'WEEK {shown:02d} / {weeks:02d}' if animated else 'PUBLIC GITHUB CALENDAR'
        ink.text((WIDTH-23, 23), caption, fill=MUTED, font=label_font, anchor='rm')
        if animated:
            head = position(cursor)
            if head:
                past = [position(cursor - 1.3 * (1 - i/18)) for i in range(19)]
                for i, (a,b) in enumerate(zip(past,past[1:])):
                    if a and b and a != b:
                        ink.line((a,b), fill=(*SIGNAL, 30 + i * 10), width=2)
                x, y = head
                ink.ellipse((x-8,y-8,x+8,y+8),fill=(*SIGNAL,48))
                ink.ellipse((x-3,y-3,x+3,y+3),fill=(*SIGNAL,255))
        return image

    output.mkdir(parents=True, exist_ok=True)
    final = frame(weeks, animated=False)
    final.save(output / 'contribution-playback-still.png', optimize=True)
    frames = [frame(weeks * i/89) for i in range(90)] + [final]
    palette = frame(weeks*.8).quantize(colors=96)
    indexed = [image.quantize(palette=palette,dither=Image.Dither.NONE) for image in frames]
    indexed[0].save(output / 'contribution-playback.gif', save_all=True,
                    append_images=indexed[1:], duration=[110]*90+[1800],
                    loop=0, optimize=True, disposal=1)
    print(f'Rendered {len(cells)} public calendar days from {first} through {last}.')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--snapshot', type=Path, help='Use a saved public calendar for an offline render.')
    args = cli.parse_args()
    render(read_calendar(args.snapshot), args.output)
