# Maya Outliner - Auto Refresh

## Overview

The Maya Outliner automatically updates when the Maya scene changes. This document explains how the auto-refresh system works and what events trigger updates.

## Supported Events

The Outliner automatically refreshes when:

### 1. Object Creation/Deletion
- ✅ Creating new objects (`polySphere`, `polyCube`, etc.)
- ✅ Deleting objects (`delete`)
- ✅ Duplicating objects (`duplicate`)

### 2. Hierarchy Changes
- ✅ Parenting objects (`parent`)
- ✅ Unparenting objects (`parent -world`)
- ✅ Grouping objects (`group`)

### 3. Object Renaming
- ✅ Renaming objects (`rename`)

### 4. Scene Operations
- ✅ Opening a scene (`file -open`)
- ✅ Creating a new scene (`file -new`)
- ✅ Undo operations (`undo`)
- ✅ Redo operations (`redo`)

### 5. Selection Changes
- ✅ Selecting objects (updates selection highlight)

## Implementation Details

### Maya Callbacks

The auto-refresh system uses Maya's OpenMaya API callbacks:

```python
# MEventMessage - High-level scene events
- SceneOpened
- NewSceneOpened
- DagObjectCreated
- Undo
- Redo
- SelectionChanged

# MDGMessage - Dependency graph events
- NodeAdded (all node creation)
- NodeRemoved (all node deletion)
- NameChanged (object renaming)

# MDagMessage - DAG hierarchy events
- ParentAdded (parenting operations)
- ParentRemoved (unparenting operations)
```

### Event Flow

```
Maya Scene Change
    ↓
Maya Callback Triggered
    ↓
on_scene_changed() called
    ↓
send_scene_update() called
    ↓
get_scene_hierarchy() fetches latest data
    ↓
webview.emit("scene_updated", hierarchy)
    ↓
Frontend receives event
    ↓
sceneData.value updated
    ↓
Vue reactivity updates UI
```

## Testing

Use the provided test script to verify auto-refresh:

```python
# In Maya Script Editor
from maya_integration import maya_outliner
outliner = maya_outliner.main()

# Run the test
import sys
sys.path.insert(0, r"C:\github\auroraview-maya-outliner")
from examples import test_auto_refresh
test_auto_refresh.test_auto_refresh()
```

The test will:
1. Create objects → Outliner should update
2. Parent objects → Outliner should update
3. Rename objects → Outliner should update
4. Delete objects → Outliner should update
5. Undo/Redo → Outliner should update

## Performance Considerations

### Callback Efficiency
- Callbacks are lightweight and non-blocking
- Updates are batched (multiple rapid changes trigger one update)
- No polling or timers required

### Update Throttling
If you experience performance issues with very large scenes:

```python
# Future enhancement: Add throttling
# Updates will be delayed by 100ms to batch rapid changes
```

## Troubleshooting

### Outliner Not Updating?

1. **Check Console Output**
   ```
   [MayaOutliner] ✓ Registered 12 Maya callbacks total
   [MayaOutliner] Scene changed, updating hierarchy...
   ```

2. **Verify Callbacks Are Active**
   ```python
   print(len(outliner.callback_ids))  # Should be > 0
   ```

3. **Check Browser Console**
   - Open DevTools (F12)
   - Look for `[App] Scene updated: X root nodes`

### Common Issues

**Issue**: Outliner updates but shows old data
- **Solution**: Check if `get_scene_hierarchy()` is returning correct data

**Issue**: Callbacks not registered
- **Solution**: Ensure Maya's OpenMaya API is available

**Issue**: Too many updates (performance)
- **Solution**: Consider adding update throttling (future enhancement)

## Code References

- **Callback Setup**: `maya_integration/maya_outliner.py:setup_maya_callbacks()`
- **Scene Update**: `maya_integration/maya_outliner.py:send_scene_update()`
- **Frontend Listener**: `src/App.vue:onMayaEvent('scene_updated')`
- **Test Script**: `examples/test_auto_refresh.py`

## Future Enhancements

- [ ] Add update throttling for large scenes
- [ ] Add option to disable auto-refresh
- [ ] Add visual feedback when updating
- [ ] Add incremental updates (only changed nodes)

