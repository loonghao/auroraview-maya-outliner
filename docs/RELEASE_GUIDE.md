# Release Guide

This document describes how to create a new release of AuroraView Maya Outliner.

## Prerequisites

- Write access to the repository
- All tests passing
- Changelog updated
- Version bumped in relevant files

## Release Process

### 1. Prepare the Release

1. **Update version numbers** in:
   - `package.json` - `version` field
   - Any other version references

2. **Update CHANGELOG.md** (if not using auto-generated changelog)
   - Add new version section
   - List all changes since last release
   - Categorize: Features, Bug Fixes, Improvements, etc.

3. **Test the build**
   ```bash
   # Build frontend
   npm run build
   
   # Test packaging
   python -m nox -s make-maya-package -- --version X.Y.Z
   
   # Verify the zip file
   # Extract and test installation
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "chore: prepare release vX.Y.Z"
   git push origin main
   ```

### 2. Create and Push Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push tag to trigger release workflow
git push origin vX.Y.Z
```

### 3. GitHub Actions Workflow

The release workflow (`.github/workflows/release.yml`) will automatically:

1. ✅ Checkout code
2. ✅ Get version from tag
3. ✅ Set up Node.js and install dependencies
4. ✅ Build frontend (`npm run build`)
5. ✅ Set up Python and install nox
6. ✅ Create Maya plugin package
7. ✅ Generate changelog
8. ✅ Create GitHub Release with:
   - Release notes
   - Changelog
   - Attached zip file

### 4. Verify Release

1. Go to [Releases](https://github.com/loonghao/auroraview-maya-outliner/releases)
2. Check that the new release is created
3. Verify the zip file is attached
4. Test download and installation

### 5. Post-Release

1. **Announce the release**
   - Update README if needed
   - Post in discussions
   - Share on social media

2. **Monitor for issues**
   - Watch for bug reports
   - Respond to user feedback

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new feature
- `v1.1.1` - Fixed bug
- `v2.0.0` - Breaking API change

## Hotfix Release

For urgent bug fixes:

1. Create hotfix branch from tag:
   ```bash
   git checkout -b hotfix/vX.Y.Z vX.Y.Z-1
   ```

2. Fix the bug and commit

3. Create new tag:
   ```bash
   git tag -a vX.Y.Z -m "Hotfix: description"
   git push origin vX.Y.Z
   ```

## Rollback

If a release has critical issues:

1. **Delete the tag** (if not yet widely distributed):
   ```bash
   git tag -d vX.Y.Z
   git push origin :refs/tags/vX.Y.Z
   ```

2. **Delete the GitHub Release**
   - Go to Releases page
   - Click "Delete" on the problematic release

3. **Fix issues and re-release** with a new patch version

## Testing Checklist

Before creating a release, verify:

- [ ] All tests pass
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Package creates successfully (`nox -s make-maya-package`)
- [ ] Installation works on Windows
- [ ] Installation works on Linux/macOS (if applicable)
- [ ] Maya integration loads without errors
- [ ] Basic functionality works (tree display, selection, visibility)
- [ ] Documentation is up to date
- [ ] CHANGELOG is updated

## Troubleshooting

### Workflow fails at build step

- Check Node.js version in workflow
- Verify all dependencies are in `package.json`
- Test build locally first

### Workflow fails at package step

- Check Python version in workflow
- Verify `noxfile.py` is correct
- Test packaging locally first

### Release created but zip file missing

- Check workflow logs for packaging errors
- Verify artifact path in workflow matches noxfile output
- Ensure `dist/` directory is created

## Manual Release (Fallback)

If GitHub Actions fails, you can create a release manually:

1. **Build and package locally**:
   ```bash
   npm run build
   python -m nox -s make-maya-package -- --version X.Y.Z
   ```

2. **Create GitHub Release**:
   - Go to Releases → "Draft a new release"
   - Choose tag: `vX.Y.Z`
   - Fill in release notes
   - Upload `dist/maya-outliner-X.Y.Z.zip`
   - Publish release

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

