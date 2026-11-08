# Profile artwork

Atomic Signal uses repository-hosted PNG panels and two six-second GIFs that animate the JR atom and oscillator. No external image service, scheduled workflow, tracking pixel, or API key is required.

- Desktop and mobile compositions are separate so the text stays readable.
- Light and dark project panels follow the browser color preference.
- The header selects a still image when reduced motion is enabled.
- Every project panel has descriptive alternative text and links to its repository.
- The expandable engineering table keeps the important project details available as ordinary Markdown.

## Regenerate

Use Python 3.11+ and install `tools/requirements.txt` in a virtual environment. Run `python tools/build_assets.py` from the repository root.

The generator uses Pillow and defaults to DejaVu Sans / DejaVu Sans Mono. Set `PROFILE_FONT` and `PROFILE_MONO_FONT` to local font-file paths to choose the typography. The published artwork uses Google Sans Flex and JetBrains Mono. Fonts are rendered into the assets and do not need to be installed by visitors.

Run `python tools/build_stack.py` with Pillow and `rsvg-convert` installed to regenerate the tech grid and contact badges. The [pinned icon sources](stack-icons/sources.tsv) come from [Skill Icons](https://github.com/tandpfun/skill-icons) and [Simple Icons](https://github.com/simple-icons/simple-icons). Their notices are in `tools/stack-icons/`.

All project descriptions are based on the linked repositories. The motion is decorative, not a live activity feed or a recording of project behavior.
