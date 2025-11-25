# Building Maya Outliner Package

## Quick Start

### 1. Build the Frontend

```bash
npm install
npm run build
```

### 2. Create the Package

```bash
python build_maya_package.py --version 0.1.0
```

This creates `dist/maya-outliner-0.1.0.zip` containing:
- ✅ Built frontend files (dist/)
- ✅ Maya integration code (auroraview_maya_outliner/)
- ✅ Correct .mod file with PYTHONPATH
- ✅ Installation scripts (install.bat, install.ps1)
- ✅ userSetup.py for auto-loading

## What's Fixed

### 1. PYTHONPATH Configuration

**Before** (broken):
```
+ MAYAVERSION:2024 auroraview-maya-outliner 0.1.0 ./
PYTHONPATH +:= .
```

**After** (working):
```
+ MAYAVERSION:2024 auroraview-maya-outliner 0.1.0 ./
PYTHONPATH +:= auroraview_maya_outliner
```

### 2. Installation Scripts

The new installation scripts:
- Copy the .mod file to Maya's modules directory
- Automatically update paths to point to the installation directory
- No manual path editing required

### 3. userSetup.py

- No more `{{PROJECT_ROOT}}` placeholder
- Works with Maya module system
- Automatically creates shelf button on Maya startup

## Installation (for end users)

1. Extract `maya-outliner-0.1.0.zip`
2. Run `install.bat` (Windows) or `install.ps1` (PowerShell)
3. Restart Maya
4. Run in Script Editor:
   ```python
   from auroraview_maya_outliner import main
   main()
   ```

Or copy `userSetup.py` to Maya scripts folder for auto-load.

## Testing the Package

After building, you can test the package locally:

```bash
# Extract to a test location
Expand-Archive -Path dist/maya-outliner-0.1.0.zip -DestinationPath C:\temp\maya-outliner-test

# Run the installer
cd C:\temp\maya-outliner-test\maya-outliner
.\install.bat

# Launch Maya and test
```

## Troubleshooting

### "No module named 'auroraview_maya_outliner'"

This means the PYTHONPATH in the .mod file is incorrect. The new build script fixes this by setting:
```
PYTHONPATH +:= auroraview_maya_outliner
```

### "No module named 'auroraview'"

Install the auroraview package:
```bash
mayapy -m pip install auroraview
```

## Development vs Production

The package supports both modes:

**Development** (default):
- Uses Vite dev server at http://localhost:5173
- Requires `npm run dev` to be running
- Hot reload enabled

**Production**:
- Uses built files from dist/
- No dev server required
- Set environment variable: `$env:AURORAVIEW_ENV='production'`

## Package Structure

```
maya-outliner-0.1.0.zip
└── maya-outliner/
    ├── auroraview_maya_outliner/    # Python code
    │   ├── __init__.py
    │   ├── maya_outliner.py
    │   └── config.py
    ├── dist/                        # Frontend
    │   ├── index.html
    │   └── assets/
    ├── maya-outliner.mod            # Module file (FIXED)
    ├── install.bat                  # Windows installer (FIXED)
    ├── install.ps1                  # PowerShell installer (FIXED)
    └── userSetup.py                 # Auto-load script (FIXED)
```

## Comparison with Old Build

| Feature | Old Build | New Build |
|---------|-----------|-----------|
| PYTHONPATH | `PYTHONPATH +:= .` ❌ | `PYTHONPATH +:= auroraview_maya_outliner` ✅ |
| Path Updates | Manual ❌ | Automatic ✅ |
| userSetup.py | Has `{{PROJECT_ROOT}}` ❌ | No placeholders ✅ |
| Shelf Button | Manual creation ❌ | Auto-created ✅ |
| Installation | Complex ❌ | Simple ✅ |

## Next Steps

After building and testing the package:

1. Tag the release:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```

2. Upload to GitHub Releases:
   - Go to https://github.com/loonghao/auroraview-maya-outliner/releases
   - Create new release
   - Upload `dist/maya-outliner-0.1.0.zip`

3. Update documentation with installation instructions

