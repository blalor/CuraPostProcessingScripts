# Cura post-processing scripts

Written with Cura 4.6.2.

## installation

Copy into your local `scripts` folder.  For me that's `~/Library/Application Support/cura/4.6/scripts`.  Restart Cura, and enable the scripts in the post-processing plugin settings.

## `EmbedSettings.py`

Embeds the settings tree into the end of the gcode as comments, which allows you
to figure out what changed between prints when fine tuning things, or if you
need to recreate your settings in the future.

Uses code lifted from the [CuraSettingsWriter](https://github.com/5axes/CuraSettingsWriter) plugin.  

### example

Partial, because the settings tree is huge.

```
;START_SETTINGS
; Job Name = 2020-07-30T06:11:43_Treefrog_TPU_cura
; Date = 2020-07-30T06:11:56.795436
; Os = Darwin Darwin Kernel Version 18.7.0: Mon Apr 27 20:09:39 PDT 2020; root:xnu-4903.278.35~1/RELEASE_X86_64
; Cura Version = 4.6.2
; Profile = flex
; Quality = Draft
; Material Extruder : 0 = TPU
; Material estimation = 6.5g
; Printing Time = 01h 09min
; >> Quality <<
; Layer Height = 0.2mm
; Initial Layer Height = 0.2mm
; Line Width = 0.4mm
;     Wall Line Width = 0.4mm
;         Outer Wall Line Width = 0.4mm
;         Inner Wall(s) Line Width = 0.4mm
;     Top/Bottom Line Width = 0.4mm
;     Infill Line Width = 0.4mm
;     Skirt/Brim Line Width = 0.4mm
;     Support Line Width = 0.4mm (disabled)
;     Support Interface Line Width = 0.4mm (disabled)
;         Support Roof Line Width = 0.4mm (disabled)
;         Support Floor Line Width = 0.4mm (disabled)
;     Prime Tower Line Width = 0.4mm (disabled)
; Initial Layer Line Width = 100.0%
…
;END_SETTINGS
```

## `PrusaM73.py`

Generates `M73` instructions, a la PrusaSlicer, so that the printer's display shows percent completed and time remaining. Uses Cura-generated `TIME:` and `TIME_ELAPSED:` comments.

### example

    ;TIME:4187
    …
    ;TIME_ELAPSED:390.755671
    M73 P9 R63
    ;LAYER:3
