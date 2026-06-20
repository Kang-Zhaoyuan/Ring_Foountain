# README image path supplement

This supplement is intended to be read together with `README.md`. It documents the local-absolute-path versus repository-relative-path convention used by COMSOL image artifacts.

## Why this file exists

Many reports in this repository were generated on the COMSOL workstation and therefore record Windows local paths such as:

```text
D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\04_moving_ring_model\images\moving_ring_velocity_magnitude_spfU.png
```

In many cases, the same artifact already exists in GitHub under the repository-relative path:

```text
04_moving_ring_model/images/moving_ring_velocity_magnitude_spfU.png
```

These two strings should normally be treated as two references to the same artifact, not as two different image versions.

## Conversion rule

Replace the local root prefix:

```text
D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\
```

with the repository root, then replace `\` with `/`.

When writing Markdown from inside `docs/`, prepend `../` before the repository-relative path. For example:

```markdown
![Stage 4 velocity](../04_moving_ring_model/images/moving_ring_velocity_magnitude_spfU.png)
```

## Canonical image index

Use these two files as the canonical index for image-path lookup:

- `docs/IMAGE_PATH_PROBE.md`: human-readable image gallery and path notes.
- `docs/image_path_probe.csv`: machine-readable local-to-repository path table.

## Collaboration rule

When adding new COMSOL images, do not create a second duplicate image only because an old report uses a Windows absolute path. First convert the local path into a repository-relative path and check whether the image already exists.
