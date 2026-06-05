# Plan: Convert PAWS from wxPython to Tkinter

## Overview

Replace all wxPython usage with Tkinter (Python stdlib). The wx dependency is
limited to three files, so the scope is manageable:

| File | wx Usage | Effort |
|---|---|---|
| `PAWS/Terminal.py` | `import wx`, `wx.App` — app bootstrap | Low |
| `PAWS/TerminalFrame.py` | Entire GUI frame (menus, text display, input, dialogs) | High |
| `PAWS/Core.py` | `import wx`, `wx.TextAttr`, `wx.Font` constants | Medium |

Game files (`Cloak.py`, `TQ.py`, `NewGame.py`) import `from PAWS.Core import *`
but never touch wx directly — **no changes needed** there.

---

## Phase 1: Core.py — Remove `import wx` and Replace wx-Specific Calls

The `ClassTerminal` class in Core.py uses wx for text styling. We need to
replace those calls with Tkinter-equivalent mechanisms.

### What changes

1. **Remove** `import wx` (line 196)
2. **`ClassTerminal.SetStyle()`** — Currently constructs a `wx.TextAttr` and
   manipulates a `wx.Font` object. Replace with Tkinter text tag approach:
   - Instead of calling `wx.TextAttr()`, `TF.SetPointSize()`, `TF.SetStyle()`,
     `TF.SetWeight()`, `TF.SetUnderlined()`, `TA.SetTextColour()`,
     `TA.SetBackgroundColour()`, `TA.SetFont()`, `TD.SetDefaultStyle(TA)`,
     build a Tkinter tag name and configure it on `Terminal.Frame.TDisplay`.
3. **Color properties** — The color name strings (`'black'`, `'blue'`, etc.)
   already use CSS/Tkinter-compatible names. No change needed.
4. **`ClassTerminal.RawOutput()`** — Calls `TD.SetEditable(True)`, `TD.AppendText()`,
   `TD.SetEditable(False)`, `TD.ScrollLines()`. Replace with Tkinter
   `Text.insert()`, `Text.config(state=...)`, `Text.see()`.
5. **`ClassTerminal.GetXY()`** — Calls `TD.PositionToXY(TD.GetInsertionPoint())`.
   Replace with Tkinter `Text.index()` parsing.
6. **`ClassTerminal.Input()`** — Reads from `Terminal.Frame.TInput.GetValue()`.
   Replace with Tkinter `Entry.get()`.
7. **`ClassTerminal.Feed()`** — Uses `Terminal.Frame.TInput.Clear()` and
   `Terminal.Frame.TInput.AppendText()`. Replace with Tkinter equivalents.
8. **`ClassTerminal.ClearScreen()`** — `Terminal.Frame.TDisplay.Clear()`.
   Replace with `Text.delete()`.
9. **`ClassTerminal.DisplayStatusLine()`** —
   `Terminal.Frame.TStatusBar.SetStatusText()`. Replace with Tkinter
   status bar label update.
10. **`ClassTerminal.Terminate()`** — Uses `Terminal.Frame.TDisplay.SetFocus()`,
    `Terminal.Frame.TInput.Enable()`, `Terminal.Frame.TInput.Clear()`,
    `Terminal.Frame.TInput.AppendText()`. All have Tkinter equivalents.

### Design Decision: Tag-based Styling

Rather than trying to mimic wx's `SetDefaultStyle`/`TextAttr` model, we'll use
Tkinter's **text tag** system, which is actually a better fit:

- Each call to `SetStyle()` generates a unique tag name (e.g. `"style_42"`)
  and configures it on `TDisplay` with the appropriate foreground, background,
  font, and style options.
- Text inserted via `RawOutput()` / `Output()` is tagged with the current
  style tag.
- `A_NORMAL` resets to the default tag.

This means `ClassTerminal` needs a `_current_tag` attribute and a `_tag_counter`
to generate unique tag names.

---

## Phase 2: TerminalFrame.py — Rewrite with Tkinter

This is the largest change. The entire file gets rewritten.

### Current wx structure

```
TFrame(wx.Frame)
├── TDisplay (wx.TextCtrl, read-only rich text display)
├── TInput   (wx.TextCtrl, single-line input)
├── TStatusBar (wx.StatusBar)
├── MenuBar
│   ├── File menu: Pick Game, Save, Restore, Debug, Log Game, Verbose, Terse, Exit
│   ├── View menu: Font…
│   └── Help menu: Hints, About PAWS
└── Event handlers for all menu items + Enter key
```

### New Tkinter structure

```python
import tkinter as tk
from tkinter import filedialog, font as tkfont

class TFrame(tk.Tk):
    """PAWS Terminal — Tkinter implementation."""

    def __init__(self):
        super().__init__()
        self.title("PAWS Terminal")
        self.geometry("829x786")

        # Menu bar
        self._create_menu()

        # Status bar
        self.TStatusBar = tk.Label(self, text="Status Bar Info Goes Here",
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.TStatusBar.pack(side=tk.BOTTOM, fill=tk.X)

        # Input field
        self.TInput = tk.Entry(self, font=("Courier", 12, "bold"))
        self.TInput.pack(side=tk.BOTTOM, fill=tk.X)
        self.TInput.bind("<Return>", self.OnTInputTextEnter)
        self.TInput.config(state=tk.DISABLED)

        # Text display
        self.TDisplay = tk.Text(self, wrap=tk.WORD, state=tk.DISABLED,
                                 font=("Arial", 12))
        self.TDisplay.pack(fill=tk.BOTH, expand=True)

        # Disable Pick Game / Save / Restore / etc until game loaded
        self._set_menu_state("disabled")
```

### Key mapping points

| wxPython | Tkinter |
|---|---|
| `wx.Frame.__init__` | `tk.Tk.__init__` |
| `wx.TextCtrl(TE_RICH2\|TE_MULTILINE\|TE_READONLY)` | `tk.Text(wrap=WORD, state=DISABLED)` |
| `wx.TextCtrl(SIMPLE_BORDER\|TE_PROCESS_ENTER)` | `tk.Entry()` + `bind("<Return>")` |
| `wx.StatusBar` | `tk.Label(relief=SUNKEN, anchor=W)` |
| `wx.MenuBar` / `wx.Menu` | `tk.Menu` |
| `wx.FileDialog` | `tkinter.filedialog.askopenfilename()` |
| `wx.FontDialog` | `tkinter.filedialog.askfont()` or a custom dialog |
| `wx.AboutDialogInfo` / `wx.AboutBox` | `tkinter.messagebox.showinfo()` |
| `wx.EVT_MENU` | `menu.add_command(command=handler)` |
| `wx.EVT_TEXT_ENTER` | `entry.bind("<Return>", handler)` |
| `TDisplay.Clear()` | `TDisplay.delete("1.0", tk.END)` |
| `TDisplay.AppendText(text)` | `TDisplay.insert(tk.END, text)` + manage state |
| `TInput.GetValue()` | `TInput.get()` |
| `TInput.Clear()` | `TInput.delete(0, tk.END)` |
| `TInput.Enable(True/False)` | `TInput.config(state=tk.NORMAL/DISABLED)` |
| `TDisplay.SetFocus()` | `TDisplay.focus_set()` |
| `self.Close()` | `self.destroy()` |
| `wx.Font(12, wx.SWISS, ...)` | `tkfont.Font(family=..., size=12, ...)` |
| `wx.TextAttr` | Tkinter text tags |

### Menu structure (preserved exactly)

All menu items and their handlers are preserved 1:1. The handler methods
(`OnMenuFileSaveMenu`, etc.) remain unchanged since they just call
`Terminal.Feed("save")` etc.

### Font dialog

wxPython had `wx.FontDialog`. Tkinter doesn't have a built-in font picker
dialog, but `tkinter.font.askfont` is not standard. Options:

1. **Skip font dialog** for now (disable View → Font menu item).
2. **Build a simple font picker** using `tkinter.font.families()` and a
   `tkinter.simpledialog`.

Recommendation: Start with option 1, add option 2 later. The font dialog
is a nice-to-have, not essential for gameplay.

### About dialog

Replace `wx.AboutBox` with `tkinter.messagebox.showinfo("About PAWS", ...)`.

---

## Phase 3: Terminal.py — Replace wx.App with Tkinter App Loop

This file is tiny (45 lines). Replace:

```python
# OLD
import wx
from . import TerminalFrame

class BoaApp(wx.App):
    def OnInit(self):
        self.main = TerminalFrame.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()
```

With:

```python
# NEW
from . import TerminalFrame

def main():
    app = TerminalFrame.TFrame()
    app.mainloop()
```

Since `TFrame` now extends `tk.Tk` instead of `wx.Frame`, this is all we need.

---

## Phase 4: Core.py — Adjust `ClassTerminal` Method Bodies

### `ClassTerminal.SetStyle()` — New Implementation

```python
def SetStyle(self, Foreground=None, Background=None, Font=None,
             FontPitch=None, IsNormal=True, IsBold=False,
             IsItalic=False, IsUnderlined=False):
    """Set terminal's default style using Tkinter text tags."""

    tag_name = f"style_{self._tag_counter}"
    self._tag_counter += 1

    # Build tag configuration
    tag_config = {}

    # Font
    font_kwargs = {}
    if self.CurrentFont:
        font_kwargs["family"] = self.CurrentFont
    font_kwargs["size"] = FontPitch if FontPitch else self.CurrentFontPitch

    if IsBold:
        font_kwargs["weight"] = "bold"
    elif IsNormal:
        font_kwargs["weight"] = "normal"

    if IsItalic:
        font_kwargs["slant"] = "italic"
    elif IsNormal:
        font_kwargs["slant"] = "roman"

    if IsUnderlined:
        font_kwargs["underline"] = True
    elif IsNormal:
        font_kwargs["underline"] = False

    tag_config["font"] = (font_kwargs.get("family", "Arial"),
                          font_kwargs.get("size", 12),
                          " ".join(k for k in ("bold", "italic")
                                   if k in font_kwargs)
                          + (" underline" if font_kwargs.get("underline") else ""))

    if Foreground:
        tag_config["foreground"] = Foreground
    if Background:
        tag_config["background"] = Background

    Terminal.Frame.TDisplay.tag_configure(tag_name, **tag_config)
    self._current_tag = tag_name
```

### `ClassTerminal.RawOutput()` — New Implementation

```python
def RawOutput(self, Text):
    TD = Terminal.Frame.TDisplay
    TD.config(state=tk.NORMAL)
    TD.insert(tk.END, Text, self._current_tag)
    TD.config(state=tk.DISABLED)
    TD.see(tk.END)
```

### Other methods — Direct mappings as described in Phase 1.

---

## Phase 5: Integration and Testing

1. **Verify imports** — Remove all `import wx` / `from wx.*` references.
   Ensure `import tkinter` (and submodules) only in the Terminal files.

2. **Smoke test with Cloak.py** — The simplest game. Launch and verify:
   - Window opens with correct layout
   - File → Pick Game loads a game module
   - Text displays with colors and styles
   - Input field accepts commands, Enter sends them
   - Save/Restore work
   - Status bar updates
   - Window closes cleanly on Exit

3. **Test with TQ.py** — More complex game. Verify same features plus:
   - Longer text output and word wrap
   - More style changes (bold, italic, colors)

4. **Check for any remaining wx references** — Grep for `wx` across all
   `.py` files and verify none remain in active code.

---

## File Change Summary

| File | Action |
|---|---|
| `PAWS/Terminal.py` | Rewrite: replace `wx.App` with `tk.Tk.mainloop()` |
| `PAWS/TerminalFrame.py` | Rewrite: full Tkinter GUI |
| `PAWS/Core.py` | Modify: remove `import wx`, replace `ClassTerminal` method bodies with Tkinter equivalents |
| `PAWS/__init__.py` | No changes |
| `Cloak.py`, `TQ.py`, `NewGame.py` | No changes |
| `main.py` | Possibly update to call `PAWS.Terminal.main()` or leave as-is |

---

## Risk Areas

1. **Text tag accumulation** — Each `SetStyle()` call creates a new tag.
   Over a long game session this could create thousands of tags. Mitigation:
   reuse tags where possible by caching tag configs keyed by
   `(foreground, background, bold, italic, underline, font_size)`.
   **Action: Implement a tag cache in `ClassTerminal`.**

2. **Tkinter mainloop vs. game loop** — The original wx code used
   event-driven input. The Tkinter `mainloop()` is also event-driven, so
   the architecture fits naturally. No blocking issues expected.

3. **Unicode** — The original code uses `encode('utf-8')` in some places
   (e.g. `Say()`). Tkinter handles Unicode natively. We should verify
   German characters (ä, ö, ü, ß) display correctly.

4. **`exec(globals())` for game loading** — This is how games are loaded
   (line 502 of TerminalFrame.py). It works regardless of GUI toolkit,
   so no change needed.

5. **Font dialog** — As noted, Tkinter lacks `wx.FontDialog`. We'll
   either skip this or build a simple custom dialog. Mark as deferred.