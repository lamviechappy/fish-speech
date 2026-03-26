"""
Preset configurations for long script generation.

This module provides predefined settings optimized for different script lengths
and use cases.
"""

from fish_speech.utils.schema import LongScriptPreset


# Predefined presets for long script generation
PRESETS = {
    "short": LongScriptPreset(
        name="short",
        description="For scripts 1000-5000 characters. No rest intervals, fast generation.",
        chunk_length=300,
        block_size=5,
        rest_interval=0.0,
    ),
    "medium": LongScriptPreset(
        name="medium",
        description="For scripts 5000-10000 characters. Light rest intervals.",
        chunk_length=250,
        block_size=5,
        rest_interval=3.0,
    ),
    "long": LongScriptPreset(
        name="long",
        description="For scripts 10000-20000 characters. Moderate rest intervals.",
        chunk_length=250,
        block_size=5,
        rest_interval=5.0,
    ),
    "very-long": LongScriptPreset(
        name="very-long",
        description="For scripts 20000+ characters (audiobooks). Conservative settings with longer rest.",
        chunk_length=200,
        block_size=3,
        rest_interval=10.0,
    ),
    "custom": LongScriptPreset(
        name="custom",
        description="Custom settings. Specify your own chunk_length, block_size, and rest_interval.",
        chunk_length=300,
        block_size=5,
        rest_interval=0.0,
    ),
}


def get_preset(preset_name: str) -> LongScriptPreset:
    """
    Get a preset configuration by name.

    Args:
        preset_name: Name of the preset (short, medium, long, very-long, custom)

    Returns:
        LongScriptPreset configuration

    Raises:
        ValueError: If preset name is not found
    """
    if preset_name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(
            f"Unknown preset '{preset_name}'. Available presets: {available}"
        )
    return PRESETS[preset_name]


def list_presets() -> list[LongScriptPreset]:
    """
    Get a list of all available presets.

    Returns:
        List of LongScriptPreset configurations
    """
    return list(PRESETS.values())


def apply_preset(request, preset_name: str):
    """
    Apply a preset configuration to a request object.

    Args:
        request: ServeLongScriptRequest object
        preset_name: Name of the preset to apply

    Returns:
        Modified request object with preset settings applied
    """
    preset = get_preset(preset_name)

    # Only apply preset if not using custom values
    if preset_name != "custom":
        request.chunk_length = preset.chunk_length
        request.block_size = preset.block_size
        request.rest_interval = preset.rest_interval

    return request
