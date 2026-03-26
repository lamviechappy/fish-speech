#!/usr/bin/env python3
"""
Example script demonstrating long script generation with presets.
"""

import requests

API_BASE = "http://127.0.0.1:8080"


def list_presets():
    """List all available presets."""
    response = requests.get(f"{API_BASE}/v1/tts/presets")
    data = response.json()

    if data["success"]:
        print("Available Presets:")
        print("-" * 80)
        for preset in data["presets"]:
            print(f"\n{preset['name'].upper()}")
            print(f"  Description: {preset['description']}")
            print(f"  Chunk Length: {preset['chunk_length']}")
            print(f"  Block Size: {preset['block_size']}")
            print(f"  Rest Interval: {preset['rest_interval']}s")
        print("-" * 80)
    else:
        print(f"Error: {data['message']}")


def generate_with_preset(text: str, preset: str, reference_id: str, output_file: str):
    """Generate audio using a preset."""
    print(f"\nGenerating with preset '{preset}'...")
    print(f"Text length: {len(text)} characters")

    response = requests.post(
        f"{API_BASE}/v1/tts/long-script",
        json={
            "text": text,
            "reference_id": reference_id,
            "preset": preset,
            "format": "wav",
        },
    )

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Audio saved to {output_file}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")


def generate_with_custom_settings(
    text: str,
    reference_id: str,
    chunk_length: int,
    block_size: int,
    rest_interval: float,
    output_file: str,
):
    """Generate audio with custom settings."""
    print(f"\nGenerating with custom settings...")
    print(f"  Chunk Length: {chunk_length}")
    print(f"  Block Size: {block_size}")
    print(f"  Rest Interval: {rest_interval}s")

    response = requests.post(
        f"{API_BASE}/v1/tts/long-script",
        json={
            "text": text,
            "reference_id": reference_id,
            "preset": "custom",
            "chunk_length": chunk_length,
            "block_size": block_size,
            "rest_interval": rest_interval,
            "format": "wav",
        },
    )

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Audio saved to {output_file}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    # List available presets
    list_presets()

    # Example texts of different lengths
    short_text = "This is a short example text. " * 50  # ~1500 chars
    medium_text = "This is a medium length example text. " * 200  # ~7600 chars
    long_text = "This is a long example text. " * 500  # ~14500 chars

    # Example 1: Short text with "short" preset
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Short text with 'short' preset")
    print("=" * 80)
    generate_with_preset(
        text=short_text,
        preset="short",
        reference_id="my-voice",
        output_file="output_short.wav",
    )

    # Example 2: Medium text with "medium" preset
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Medium text with 'medium' preset")
    print("=" * 80)
    generate_with_preset(
        text=medium_text,
        preset="medium",
        reference_id="my-voice",
        output_file="output_medium.wav",
    )

    # Example 3: Long text with "long" preset
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Long text with 'long' preset")
    print("=" * 80)
    generate_with_preset(
        text=long_text,
        preset="long",
        reference_id="my-voice",
        output_file="output_long.wav",
    )

    # Example 4: Custom settings
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom settings")
    print("=" * 80)
    generate_with_custom_settings(
        text=medium_text,
        reference_id="my-voice",
        chunk_length=250,
        block_size=4,
        rest_interval=7.0,
        output_file="output_custom.wav",
    )

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
