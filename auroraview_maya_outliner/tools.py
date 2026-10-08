"""Explicit shared tools over the existing Maya scene API."""


def create_tools(scene, subscribe=None):
    """Create an owner for UI binding or attachment to a borrowed Core server.

    Create, call and close it on Maya's main thread. The caller owns the scene,
    event source, dispatcher and service; this factory starts none of them.
    """
    from auroraview_dcc_mcp import Tool, ToolSet

    def snapshot():
        return {
            "hierarchy": scene.get_scene_hierarchy(),
            "selection": scene.get_selection(),
        }

    scene_schema = {
        "type": "object",
        "properties": {
            "hierarchy": {"type": "array", "items": {"type": "object"}},
            "selection": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["hierarchy", "selection"],
        "additionalProperties": False,
    }
    return ToolSet(
        "maya-outliner",
        [
            Tool(
                "scene.snapshot",
                "Read Maya hierarchy and selection using full DAG paths",
                {"type": "object", "additionalProperties": False},
                snapshot,
                output_schema=scene_schema,
                read_only=True,
                destructive=False,
                idempotent=True,
            ),
            Tool(
                "scene.rename",
                "Rename one unambiguous Maya node and read back the scene",
                {
                    "type": "object",
                    "properties": {
                        "old_name": {"type": "string", "minLength": 1},
                        "new_name": {"type": "string", "minLength": 1, "pattern": "^[^|]+$"},
                    },
                    "required": ["old_name", "new_name"],
                    "additionalProperties": False,
                },
                scene.rename_node,
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "object",
                            "properties": {"ok": {"const": True}, "node": {"type": "string"}},
                            "required": ["ok", "node"],
                            "additionalProperties": False,
                        },
                        "scene": scene_schema,
                    },
                    "required": ["result", "scene"],
                    "additionalProperties": False,
                },
                readback=snapshot,
                destructive=True,
            ),
        ],
        description="Maya Outliner scene tools shared by an explicit UI and agent binding",
        dcc="maya",
        subscribe=subscribe,
    )
