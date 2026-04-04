## Exercise Pack Addition: [Pack Name]

Closes #[issue number]

### Pack summary

- **Pack name:** 
- **Author / maintainer:** 
- **Target muscle groups:** 
- **Number of exercises:** 
- **Intensity range:** 1 (gentle) – 3 (vigorous)
- **Research sources cited:** (list DOI or URL for each exercise)

### Pack file location

`exercise_packs/[pack_name]/pack.toml`

### Validation

- [ ] `active-pauses validate-pack exercise_packs/[pack_name]/pack.toml` exits 0
- [ ] All exercises have `research_source` field with valid citation
- [ ] All exercises with intensity ≥ 2 have at least one `contraindication` listed
- [ ] Animation reference files exist in `assets/animations/` or pack includes its own
- [ ] Verbal cue text (`verbal_cue`) is under 120 characters per phase
- [ ] No `exec`, `import`, `script`, `shell` keys present anywhere in TOML files

### Testing

- [ ] Pack loads without error via `active-pauses list-exercises --pack [pack_name]`
- [ ] At least 2 exercises manually triggered via `active-pauses trigger [exercise_id]` and tested in exercise window
- [ ] `pytest tests/unit/test_exercise_loader.py -v` passes with new pack

### Screenshots

<!-- Required: screenshot of at least one exercise running in the GTK window with avatar animation. -->

### Checklist

- [ ] All exercises reviewed for medical accuracy by contributor (note: not a substitute for professional medical advice)
- [ ] Contraindications are conservative (err on the side of caution)
- [ ] Exercise names are unique across all packs
- [ ] License for any referenced material is compatible with MIT
