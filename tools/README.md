# Profile artwork

Atomic Signal uses repository-hosted PNG panels and two versions of a 24-second header loop. Three seeded signal channels share a baseline and produce bursts that vary in timing, amplitude, width, and frequency.

- Desktop and mobile compositions are separate so the text stays readable.
- Light and dark project panels follow the browser color preference.
- The header selects a still image when reduced motion is enabled.
- Every project panel has descriptive alternative text and links to its repository.
- The expandable engineering table keeps the important project details available as ordinary Markdown.

## Regenerate

Use Python 3.11+ and install `tools/requirements.txt` in a virtual environment. Run `python tools/build_assets.py` from the repository root.

The generator uses Pillow and defaults to DejaVu Sans / DejaVu Sans Mono. Set `PROFILE_FONT` and `PROFILE_MONO_FONT` to local font-file paths to choose the typography. The published artwork uses Google Sans Flex and JetBrains Mono. Fonts are rendered into the assets and do not need to be installed by visitors.

Run `python tools/build_profile_panels.py` to regenerate the focus, experience, engineering principles, and closing motto artwork with the same fonts.

Run `python tools/build_stack.py` with Pillow and `rsvg-convert` installed to regenerate the tech grid, contact buttons, and certification badges. The [pinned icon sources](stack-icons/sources.tsv) come from [Skill Icons](https://github.com/tandpfun/skill-icons), [Simple Icons](https://github.com/simple-icons/simple-icons), and [Langfuse](https://github.com/langfuse/langfuse). Their notices are in `tools/stack-icons/`.

All project descriptions are based on the linked repositories. The motion is decorative, not a live activity feed or a recording of project behavior.

## Contribution activity

The contribution animation reads the date and activity level of each day from the public GitHub calendar. The waveform header and the contribution animation are separate assets. The animation reveals each week and traces its active days in date order. GitHub Actions publishes the GIF and a reduced-motion still to GitHub Pages daily and supports a manual refresh. Refreshes deploy image files without making commits or using a personal token.

For a local refresh, run `python tools/build_contribution_playback.py --output path/to/output` with Pillow installed. If GitHub changes the calendar markup or the fetch fails, the workflow stops and the last published images remain available.
