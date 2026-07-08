## Avatar / Animation Asset: [Description]

Closes #[issue number]

### Asset type

- [ ] New base body variant (gender expression + skin tone)
- [ ] New muscle highlight overlay
- [ ] New clothing layer
- [ ] New face/hair variant
- [ ] New CSS animation (exercise animation)
- [ ] New audio cue

### Files added

<!-- List exact file paths -->

### Naming convention compliance

- [ ] Base body: `body_[expr]_s[1-5].svg` where `expr` ∈ {`masc`, `femm`, `nbin`}
- [ ] Overlay: `highlight_[muscle_group].svg`
- [ ] Animation CSS: `[muscle_group]_[exercise_slug].css`
- [ ] Animation class name in CSS matches `anim-[exercise_id]` convention
- [ ] Audio: `.ogg` format, ≤50ms silence at start/end, ≤200KB

### SVG compliance (for SVG assets)

- [ ] SVG uses `id` attributes on all animatable layers (format: `layer-[name]`)
- [ ] SVG viewBox is `0 0 200 400` (standard avatar canvas)
- [ ] No embedded raster images (pure vector)
- [ ] File size ≤ 50KB (before gzip)
- [ ] Tested in Firefox and Chromium SVG renderer

### CSS animation compliance (for animation CSS)

- [ ] `@media (prefers-reduced-motion: reduce)` block present with static fallback
- [ ] Animation uses `transform` and `opacity` only (no layout-triggering properties)
- [ ] Keyframe names follow `kf-[exercise_id]-[phase]` convention
- [ ] Tested at 30fps minimum on integrated graphics

### Screenshots / previews

<!-- Required: screenshot or short video of the asset rendered in the exercise window. -->

### Checklist

- [ ] Asset is original work or licensed CC0/CC-BY compatible with MIT project
- [ ] Attribution added to `assets/[type]/README.md` if required by license
- [ ] No proprietary fonts or icons embedded in SVG
