# UVPin Global
Maya tool to add and manage uvPin systems

Last version: 0 - tested in Maya 2024-2026

For more details make sure to read the wiki! https://github.com/JulienRogar/UVPinGlobal/wiki

Changelog: https://github.com/JulienRogar/UVPinGlobal/wiki/Changelog

## How to use
The tool works with instances, each instance has it's own data and window allowing to have multiple usages in same time

## How to install
_Requires Maya's default Python package_

-Download the `UVPin_Global.py` file
\
\
-Move the file to one of Maya's script folders\
(Script folders in Maya preferences folder are by default at `C:\Users\...\Documents\maya\scripts` or for each Maya version `C:\Users\...\Documents\maya\VERSION\scripts` as `C:\Users\...\Documents\maya\2024\scripts`)
\
\
-Paste bottom code in a Python tab inside Maya's script editor
>import UVPin_Global\
UVPin_Global.Load( multi_windows=True, keep_win_pref=False, tab=1 )
<img width="631" height="327" alt="Script inside Script editor UI" src="https://github.com/user-attachments/assets/64c294a5-ed2b-427d-84fd-bf4a838e0358" />

-Select all the code and press the excecute button or drag and drop it on the shelf to set it as a shelf button to create a new instance/window at each press
\
\
\
You can use similarly other [module's public commands](https://github.com/JulienRogar/Local-MotionTrail/wiki#public-commands) with only `UVPin_Global.command()` where **command()** is the command and it's argument(s) between parenthesis
