"""Render the profile's text panels using the Atomic Signal artwork primitives."""

from PIL import ImageDraw

from build_assets import ASSETS, BG, LINE, MUTE, PANEL, S, WHITE, canvas, font, panel, rect, text


INTRO_LEAD = 'I build across AI, retrieval, and cloud infrastructure,'
INTRO_BODY = 'with a soft spot for systems that can explain a decision, recover from a mistake, and hold up under scrutiny.'
EXPERIENCE = (
    ('GenAI Intern', 'Tata Consultancy Services', 'Jun–Jul 2026',
     'Worked on RAG search, prompt-injection guardrails, and Langfuse tracing.'),
    ('SAP Analytics Cloud Intern', 'Blueprint Technologies', 'May–Jul 2025',
     'Built SAP Analytics Cloud dashboards and predictive models.'),
)
WORK_LEAD = 'Useful intelligence needs good systems around it.'
WORK_BODY = 'That means fresh evidence for retrieval, explicit constraints for scheduling, reversible operations for personal data, and honest evaluation for learned policies.'
MOTTO = ('Be kind. Stay curious.', 'Build something worth understanding.')


def width_of(value, size, bold=False, mono=False):
    return font(size, bold, mono).getlength(value)/S


def wrap(value, max_width, size, bold=False):
    lines = []
    current = ''
    for word in value.split():
        candidate = f'{current} {word}' if current else word
        if current and width_of(candidate, size, bold) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return [*lines, current]


def write_lines(draw, x, y, lines, size, spacing, ink, bold=False):
    for index, value in enumerate(lines):
        text(draw, (x,y+index*spacing), value, size, ink, bold)


def box(draw, width, y, height, surface, border, shadow, accent):
    panel(draw,8,y+2,width-16,height-9,border,surface,shadow)
    rect(draw,(9,y+3,14,y+height-8),accent)


def save(image, name, light, mobile):
    variant = ('-mobile' if mobile else '') + ('-light' if light else '')
    image.save(ASSETS/f'atomic-{name}{variant}.png', optimize=True)


def prose(name, label, lead, body, mobile, light, theme, accent):
    bg, surface, ink, muted, border, shadow = theme
    width = 568 if mobile else 928
    lead_size, body_size = (35,26) if mobile else (29,20)
    lead_step, body_step = (42,34) if mobile else (36,27)
    max_width = width-76
    lead_lines = wrap(lead,max_width,lead_size,True)
    body_lines = wrap(body,max_width,body_size)
    body_y = 54 + len(lead_lines)*lead_step + 6
    height = body_y + len(body_lines)*body_step + 22
    image = canvas(width,height,bg)
    draw = ImageDraw.Draw(image)
    box(draw,width,0,height,surface,border,shadow,accent)
    text(draw,(36,22),label,14 if mobile else 11,accent,mono=True)
    write_lines(draw,36,54,lead_lines,lead_size,lead_step,ink,True)
    write_lines(draw,36,body_y,body_lines,body_size,body_step,muted)
    save(image,name,light,mobile)


def experience(mobile, light, theme, accents):
    bg, surface, ink, muted, border, shadow = theme
    width = 568 if mobile else 928
    title_size, company_size, body_size = (34,25,25) if mobile else (25,20,19)
    title_step, body_step = (42,32) if mobile else (32,25)
    chip_size = 15 if mobile else 12
    specs = []
    for role, company, date, description in EXPERIENCE:
        title = wrap(role,width-76,title_size,True)
        body = wrap(description,width-76,body_size)
        company_y = 22 + len(title)*title_step + 2
        body_y = company_y + company_size + 12
        specs.append((title,company,date,body,company_y,body_y,body_y+len(body)*body_step+22))

    image = canvas(width,sum(spec[-1] for spec in specs)+8,bg)
    draw = ImageDraw.Draw(image)
    y = 0
    for (title,company,date,body,company_y,body_y,height), accent in zip(specs,accents):
        box(draw,width,y,height,surface,border,shadow,accent)
        write_lines(draw,36,y+22,title,title_size,title_step,ink,True)
        text(draw,(36,y+company_y),company,company_size,accent,True)
        chip_width = width_of(date,chip_size,mono=True) + 24
        chip_x = width-36-chip_width
        chip_y = y+company_y-1
        if width_of(company,company_size,True)+54 > chip_x:
            chip_y = y+21
        rect(draw,(chip_x,chip_y,width-36,chip_y+chip_size+12),bg,border)
        text(draw,(chip_x+12,chip_y+4),date,chip_size,accent,mono=True)
        write_lines(draw,36,y+body_y,body,body_size,body_step,muted)
        y += height+8
    save(image,'experience',light,mobile)


def motto(mobile, light, theme, accent):
    bg, surface, ink, _, border, shadow = theme
    width = 568 if mobile else 928
    title_size, body_size = (42,36) if mobile else (36,31)
    body_step = 44 if mobile else 38
    lines = wrap(MOTTO[1],width-84,body_size,True)
    height = 78+len(lines)*body_step+20
    image = canvas(width,height,bg)
    draw = ImageDraw.Draw(image)
    box(draw,width,0,height,surface,border,shadow,accent)
    text(draw,((width-width_of(MOTTO[0],title_size,True))/2,20),MOTTO[0],title_size,accent,True)
    for index, value in enumerate(lines):
        x = (width-width_of(value,body_size,True))/2
        text(draw,(x,78+index*body_step),value,body_size,ink,True)
    save(image,'motto',light,mobile)


if __name__ == '__main__':
    for light in (False,True):
        theme = ('#f4f6f1','#f7f8f4','#172022','#45534e','#b6c1b8','#d4dbd2') if light else (BG,PANEL,WHITE,MUTE,LINE,'#030606')
        lime, cyan, violet = ('#50691c','#24697b','#684da1') if light else ('#e7ff58','#8bded3','#c2adff')
        for mobile in (False,True):
            prose('focus','FOCUS',INTRO_LEAD,INTRO_BODY,mobile,light,theme,lime)
            experience(mobile,light,theme,(cyan,violet))
            prose('work','WHAT CONNECTS THE WORK',WORK_LEAD,WORK_BODY,mobile,light,theme,violet)
            motto(mobile,light,theme,lime)
