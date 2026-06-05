# Python 2 → 3 Compatibility Issues in PAWS

## Breaking Issues (will cause runtime crashes)

| # | File | Line | Problem | Python 3 Fix |
|---|------|------|---------|-------------|
| 1 | Core.py | 2148-2149 | `.encode('utf-8')` produces `bytes`, but files are opened in text mode. Writing bytes to a text-mode file raises `TypeError` | Remove `.encode('utf-8')` |
| 2 | Universe.py | 6705 | `.encode()` on a `str` in a `%` format string produces `bytes`, which will display as `b'TQ'` or crash | Remove `.encode()` |

## Non-Breaking but Should-Be-Fixed Issues

### `== None` / `!= None` instead of `is None` / `is not None`

Works in Python 3 but not PEP 8 compliant. 24 instances across Core.py and Universe.py.

Examples:
- `Core.py, line 1210`: `if Object == None: return`
- `Core.py, line 1350`: `if Actor == None:`
- `Core.py, line 2166`: `if Sentence == None: return Sentence`
- `Universe.py, line 386`: `if Object.StartingLocation != None:`
- `Universe.py, line 2987`: `if self.Location != None:`

**Fix**: Replace `== None` with `is None` and `!= None` with `is not None`

### `type(x) == type(y)` instead of `isinstance()`

Works in Python 3 but not Pythonic, and fails for subclasses. 12 instances.

**String type checks** (should use `isinstance(x, str)`):
- `Core.py, line 2167`: `if type(Sentence) != type(""): return Sentence`
- `TerminalFrame.py, line 662`: `if type(Text) != type(""): Text = repr(Text)`
- `TerminalFrame.py, line 683`: `if type(Expr) != type(""): Expr = repr(Expr)`
- `Universe.py, line 4365`: `if type(NewRoom) == type(""):`
- `Universe.py, line 4409`: `if type(NewRoom) == type(""):`
- `Universe.py, line 4453`: `if type(NewRoom) == type(""):`

**List type checks** (should use `isinstance(x, list)`):
- `Core.py, line 1245`: `if type(List) != type([]): continue`
- `Core.py, line 1517`: `if type(List) == type([]):`
- `Universe.py, line 5575`: `if type(Object) == type([]):`
- `Universe.py, line 5588`: `if type(Object) == type([]):`

**Function type checks** (should use `callable()` or `inspect.isfunction()`):
- `Core.py, line 2248`: `if type(DaemonFuse) != type(StartDaemon): return FAILURE`
- `Core.py, line 2300`: `if type(DaemonFuse) != type(StartDaemon): return FAILURE`

### Bare `except:` clauses

Catches all exceptions including `SystemExit` and `KeyboardInterrupt`. Should be `except Exception:` at minimum. 7 instances:

- `Core.py, line 544`: `except: pass`
- `Core.py, line 1614`: `except: Say("Syntax Error In CodeString")`
- `TerminalFrame.py, line 575`: `except:`
- `TerminalFrame.py, line 614`: `except: pass`
- `TerminalFrame.py, line 635`: `except:`
- `TerminalFrame.py, line 684`: `except:`
- `Universe.py, line 6710`: `except:`

### Redundant `u""` string prefixes

Valid in Python 3.3+ but unnecessary. ~10 instances in Cloak.py, Universe.py, and TQ.py.

Examples:
- `Cloak.py, line 546`: `u" with a cloak hanging on it,"`
- `Universe.py, line 4169`: `{Agree(u'have')}`

### Redundant `float()` wrapper around division

- `Universe.py, line 585`: `if random.random() < float(percent/100.0):`
- In Python 3, `/` always does float division, so `float()` is unnecessary
- **Fix**: `if random.random() < percent/100:`

### `types.MethodType` comparison

- `Core.py, line 486`: `if type(getattr(self,Attribute)) != types.MethodType:`
- Works in Python 3 but semantics differ slightly (unbound methods are just functions in Py3)
- **Better approach**: Use `callable()` and check for properties via `isinstance`

## Already Fixed (Python 2 remnants remain as comments)

| Pattern | File | Line(s) | Current Status |
|---------|------|----------|---------------|
| `string.strip()` | Universe.py | 162 | Fixed → `Verb.strip()` |
| `string.capitalize()` | Universe.py | 2876 | Fixed → `Attr.capitalize()` |
| `string.join()` | Universe.py | 3714, 5632, 5646, 6146, 6796, 6811 | Fixed → `", ".join(list)` |
| `string.replace()` | Universe.py | 6508, 6509 | Fixed → `str.replace()` |
| `string.replace()` | Core.py | 1899, 1979, 1980 | Fixed → `str.replace()` |
| `string.split()` | Core.py | 1908 | Fixed → `str.split()` |
| `import six` | Core.py | 193 | Removed (was dead import) |
| `types.InstanceType` | Core.py | 396 | Already replaced with `isinstance()` (old line commented out) |
| `string.split()` | Core.py | 1077, 4241, 4255, 4321 | Already replaced (old lines commented out) |
| `string.join()` | Universe.py | 1306 | Already replaced (old line commented out) |
| `string.ljust()` | Universe.py | 337 | Already replaced (old line commented out) |
| `import wx` | Core.py, Terminal.py, TerminalFrame.py | multiple | Replaced with `import tkinter as tk` |

## Not an Issue

- `u""` string prefixes — valid in Python 3.3+
- Old-style class `class ClassFundamental:` — equivalent to `class ClassFundamental(object):` in Python 3
- `import string` — still valid; used for `string.punctuation`
- `exec(STMT, globals())` — already using function-call syntax
- `from __future__` imports — none present
- `dict.has_key()` — not used; all checks use `in`
- `dict.iteritems()` / `dict.itervalues()` / `dict.iterkeys()` — not used; all use `.items()`
- `xrange()` — not used; all loops use `range()`
- `raw_input()` — not used
- `print` statement — all use function-call syntax