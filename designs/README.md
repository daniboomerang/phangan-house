# Designs

Ana's files go here. **IFC preferred** — every serious tool exports it, and it
carries storey levels and element types rather than just shapes.

`derived/` holds what the scripts extract: geometry, levels, and a compliance
report against the terrain in `land/` and the limits in
`skills/thai-hillside-law/`.

Large binaries are gitignored. If an IFC export exceeds 100 MB, ask for
per-storey or geometry-only, or enable Git LFS.

## The placement problem

An IFC usually sits at its own local origin, not on the site. Something has to
map it onto UTM 47N. Three ways, best first:

1. Ana sets the IFC georeference properly in her tool
2. A known point in the model maps to one of the survey markers
3. Manual offset and rotation, recorded once and reused

**This is the real work in importing.** Parsing is solved — `ifcopenshell` reads
IFC, `ezdxf` reads DXF, `trimesh` reads OBJ/DAE/glTF, and `web-ifc` parses IFC
in the browser with no upload at all.
