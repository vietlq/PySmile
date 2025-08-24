#!/usr/bin/env python

"""
@author             Le Quoc Viet <viet@code2.pro>
@version            0.6
@brief              Convert image formats, resize images in batches using Typer CLI
@description        Modern CLI for batch image processing with type hints and better UX
@modified           August 2025

# The last modificaton was May 1, 2017 and the previous version was 0.5
"""

import os
import glob
from pathlib import Path
from typing import List, Optional, Tuple
from enum import Enum

import typer
from PIL import Image
from rich.console import Console
from rich.progress import track
from rich.table import Table

# Import your custom utilities (you'll need to install/create this)
# from pysmile.image_conv_util import convert_to_palette, pure_pil_alpha_to_color_v2

console = Console()


class OutputFormat(str, Enum):
    png = "png"
    gif = "gif"
    jpg = "jpg"
    jpeg = "jpeg"
    bmp = "bmp"
    pdf = "pdf"


class ResizeMode(str, Enum):
    ratio = "ratio"
    width = "width"
    height = "height"


app = typer.Typer(
    name="image-converter",
    help="🖼️  Batch convert and resize images with style!",
    rich_markup_mode="rich",
)


# Fallback functions if pysmile is not available
def convert_to_palette(image: Image.Image) -> Image.Image:
    """Convert RGBA image to palette mode for GIF transparency."""
    # Simple fallback - you can implement the full logic or install pysmile
    return image.convert("P", palette=Image.ADAPTIVE, colors=255)


def pure_pil_alpha_to_color_v2(
    image: Image.Image, color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """Convert RGBA to RGB with specified background color."""
    if image.mode != "RGBA":
        return image

    background = Image.new("RGB", image.size, color)
    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
    return background


def get_matched_files(patterns: List[str]) -> List[Path]:
    """Get all files matching the given patterns."""
    files = []
    for pattern in patterns:
        # Expand ~ to home directory
        expanded_pattern = os.path.expanduser(pattern)
        matched = glob.glob(expanded_pattern)
        files.extend([Path(f) for f in matched if Path(f).is_file()])

    return list(set(files))  # Remove duplicates


def resize_image(image: Image.Image, mode: ResizeMode, value: int) -> Image.Image:
    """Resize image based on the specified mode and value."""
    width, height = image.size

    if mode == ResizeMode.ratio:
        if value != 100:
            new_size = (int(width * value / 100), int(height * value / 100))
            image.thumbnail(new_size, Image.Resampling.LANCZOS)

    elif mode == ResizeMode.width:
        if width != value:
            ratio = value / width
            new_size = (value, int(height * ratio))
            image.thumbnail(new_size, Image.Resampling.LANCZOS)

    elif mode == ResizeMode.height:
        if height != value:
            ratio = value / height
            new_size = (int(width * ratio), value)
            image.thumbnail(new_size, Image.Resampling.LANCZOS)

    return image


def save_image(
    image: Image.Image,
    output_path: Path,
    format: Optional[OutputFormat],
    preserve_gif_transparency: bool,
):
    """Save image with proper format handling."""

    if format == OutputFormat.png:
        # Preserve PNG metadata
        png_info = image.info
        image.save(output_path, **png_info)

    elif format == OutputFormat.gif and preserve_gif_transparency:
        if image.mode == "P":
            if "transparency" in image.info:
                image.save(output_path, transparency=image.info["transparency"])
            else:
                image.save(output_path)
        elif image.mode == "RGBA":
            image = convert_to_palette(image)
            image.save(output_path, transparency=255)
        else:
            image.save(output_path)

    elif format in (
        OutputFormat.pdf,
        OutputFormat.jpg,
        OutputFormat.jpeg,
        OutputFormat.bmp,
        OutputFormat.gif,
    ):
        if image.mode == "RGBA":
            image = pure_pil_alpha_to_color_v2(image)
        image.save(output_path)

    else:
        image.save(output_path)


@app.command()
def convert(
    patterns: List[str] = typer.Argument(
        ..., help="File patterns to match (e.g., '*.png', 'photos/*.jpg')"
    ),
    dest_dir: Path = typer.Option(
        Path.cwd(),
        "--dest-dir",
        "-d",
        help="Destination directory for processed images",
        file_okay=False,
        dir_okay=True,
    ),
    output_format: Optional[OutputFormat] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format for all images. If not specified, original format is preserved.",
    ),
    resize_ratio: Optional[int] = typer.Option(
        None,
        "--ratio",
        "-r",
        help="Resize ratio in percentage (e.g., 50 for half size)",
        min=1,
        max=1000,
    ),
    width: Optional[int] = typer.Option(
        None,
        "--width",
        "-w",
        help="Resize to specific width (maintains aspect ratio)",
        min=1,
    ),
    height: Optional[int] = typer.Option(
        None,
        "--height",
        "-h",
        help="Resize to specific height (maintains aspect ratio)",
        min=1,
    ),
    gif_transparency: bool = typer.Option(
        False,
        "--gif-transparency",
        "-t",
        help="Preserve transparency when converting to GIF",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Process without confirmation"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be processed without actually doing it",
    ),
):
    """
    🖼️ Batch convert and resize images.

    Examples:
        image-converter convert "*.jpg" --format png --ratio 50
        image-converter convert "photos/*.png" --width 800 -d ./thumbnails
        image-converter convert "*.gif" --height 200 --gif-transparency
    """

    # Validate mutually exclusive resize options
    resize_options = [resize_ratio, width, height]
    if sum(x is not None for x in resize_options) > 1:
        console.print(
            "[red]Error: Only one resize option can be specified at a time![/red]"
        )
        raise typer.Exit(1)

    # Determine resize mode and value
    resize_mode = None
    resize_value = None

    if resize_ratio is not None:
        resize_mode = ResizeMode.ratio
        resize_value = resize_ratio
    elif width is not None:
        resize_mode = ResizeMode.width
        resize_value = width
    elif height is not None:
        resize_mode = ResizeMode.height
        resize_value = height

    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Check write permissions
    if not os.access(dest_dir, os.W_OK):
        console.print(
            f"[red]Error: No write permission for directory: {dest_dir}[/red]"
        )
        raise typer.Exit(1)

    # Find matching files
    console.print("🔍 Finding matching files...")
    matched_files = get_matched_files(patterns)

    if not matched_files:
        console.print(
            "[yellow]No files found matching the specified patterns.[/yellow]"
        )
        raise typer.Exit(0)

    # Show summary
    table = Table(title="Processing Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Files found", str(len(matched_files)))
    table.add_row("Destination", str(dest_dir.absolute()))
    table.add_row(
        "Output format", output_format.value if output_format else "Keep original"
    )

    if resize_mode:
        table.add_row("Resize", f"{resize_mode.value}: {resize_value}")
    else:
        table.add_row("Resize", "No resizing")

    table.add_row("GIF transparency", "Yes" if gif_transparency else "No")

    console.print(table)

    # Show file list if not too many
    if len(matched_files) <= 10:
        console.print("\n📁 Files to process:")
        for file in matched_files:
            console.print(f"  • {file.name}")
    elif not quiet:
        console.print(f"\n📁 {len(matched_files)} files to process (too many to list)")

    # Confirm unless quiet mode or dry run
    if not quiet and not dry_run:
        if not typer.confirm("\n🚀 Proceed with processing?"):
            console.print("Operation cancelled.")
            raise typer.Exit(0)

    if dry_run:
        console.print(
            "\n[yellow]Dry run completed. No files were actually processed.[/yellow]"
        )
        raise typer.Exit(0)

    # Process files
    console.print(f"\n🎨 Processing {len(matched_files)} files...")

    success_count = 0
    error_count = 0

    for file_path in track(matched_files, description="Converting..."):
        try:
            # Determine output filename
            if output_format:
                output_filename = file_path.stem + f".{output_format.value}"
            else:
                output_filename = file_path.name

            output_path = dest_dir / output_filename

            # Open and process image
            with Image.open(file_path) as image:
                # Resize if needed
                if resize_mode:
                    image = resize_image(image, resize_mode, resize_value)

                # Save with proper format handling
                save_image(image, output_path, output_format, gif_transparency)

            success_count += 1

        except Exception as e:
            console.print(f"[red]Error processing {file_path.name}: {str(e)}[/red]")
            error_count += 1

    # Final summary
    if success_count > 0:
        console.print(
            f"\n[green]✅ Successfully processed {success_count} files![/green]"
        )
    if error_count > 0:
        console.print(f"[red]❌ Failed to process {error_count} files.[/red]")

    console.print(f"📂 Output saved to: {dest_dir.absolute()}")


@app.command()
def info(patterns: List[str] = typer.Argument(..., help="File patterns to analyze")):
    """📊 Show information about matching image files."""

    matched_files = get_matched_files(patterns)

    if not matched_files:
        console.print(
            "[yellow]No files found matching the specified patterns.[/yellow]"
        )
        raise typer.Exit(0)

    table = Table(title="Image Files Information")
    table.add_column("File", style="cyan")
    table.add_column("Format", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Mode", style="magenta")

    for file_path in matched_files:
        try:
            with Image.open(file_path) as image:
                table.add_row(
                    file_path.name,
                    image.format or "Unknown",
                    f"{image.size[0]}x{image.size[1]}",
                    image.mode,
                )
        except Exception as e:
            table.add_row(file_path.name, "Error", str(e), "")

    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
