#!/usr/bin/env python3
"""
Convert Lanelet2 OSM map to OpenDrive format.

This script performs a two-step conversion:
1. Lanelet2 OSM -> CommonRoad XML
2. CommonRoad XML -> OpenDrive XODR

Usage:
    python convert_lanelet2_to_opendrive.py <input.osm> [output.xodr]
    python convert_lanelet2_to_opendrive.py <input.osm> -o <output.xodr>

Examples:
    python convert_lanelet2_to_opendrive.py input.osm
    python convert_lanelet2_to_opendrive.py input.osm output.xodr
    python convert_lanelet2_to_opendrive.py input.osm -o output.xodr --no-keep-temp
"""

import argparse
from pathlib import Path
import sys

from crdesigner.map_conversion.map_conversion_interface import (
    lanelet_to_commonroad,
    commonroad_to_opendrive
)
from crdesigner.common.file_writer import CRDesignerFileWriter
from commonroad.planning.planning_problem import PlanningProblemSet


def convert_lanelet2_to_opendrive(
    input_osm_path: str,
    output_xodr_path: str,
    temp_cr_path: str = None,
    keep_temp: bool = True
):
    """
    Convert Lanelet2 OSM file to OpenDrive format.

    Args:
        input_osm_path: Path to input Lanelet2 OSM file
        output_xodr_path: Path to output OpenDrive XODR file
        temp_cr_path: Path to temporary CommonRoad XML file (optional)
        keep_temp: Whether to keep the temporary CommonRoad file (default: True)
    """
    input_path = Path(input_osm_path)
    output_path = Path(output_xodr_path)

    # Set temporary file path
    if temp_cr_path is None:
        temp_path = input_path.with_suffix('.xml')
    else:
        temp_path = Path(temp_cr_path)

    print(f"Starting conversion process...")
    print(f"Input:  {input_path}")
    print(f"Temp:   {temp_path}")
    print(f"Output: {output_path}")
    print("-" * 60)

    # Step 1: Lanelet2 OSM -> CommonRoad
    print("\n[Step 1/2] Converting Lanelet2 OSM to CommonRoad...")
    try:
        scenario = lanelet_to_commonroad(str(input_path))
        print(f"  ✓ Successfully converted to CommonRoad scenario")
        print(f"  - Lanelets: {len(scenario.lanelet_network.lanelets)}")
        print(f"  - Traffic signs: {len(scenario.lanelet_network.traffic_signs)}")
        print(f"  - Traffic lights: {len(scenario.lanelet_network.traffic_lights)}")
    except Exception as e:
        print(f"  ✗ Error during Lanelet2 to CommonRoad conversion:")
        print(f"    {type(e).__name__}: {e}")
        sys.exit(1)

    # Save temporary CommonRoad file
    print(f"\n  Saving temporary CommonRoad file to: {temp_path}")
    try:
        from commonroad.common.writer.file_writer_interface import OverwriteExistingFile
        from commonroad.scenario.scenario import Tag
        writer = CRDesignerFileWriter(
            scenario=scenario,
            planning_problem_set=PlanningProblemSet(),
            author="Map Conversion Script",
            affiliation="CommonRoad Scenario Designer",
            source="Lanelet2 OSM",
            tags=set()
        )
        writer.write_to_file(str(temp_path), overwrite_existing_file=OverwriteExistingFile.ALWAYS)
        print(f"  ✓ CommonRoad XML saved successfully")
    except Exception as e:
        print(f"  ✗ Error saving CommonRoad file:")
        print(f"    {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 2: CommonRoad -> OpenDrive
    print(f"\n[Step 2/2] Converting CommonRoad to OpenDrive...")
    try:
        commonroad_to_opendrive(temp_path, output_path)
        print(f"  ✓ Successfully converted to OpenDrive")
        print(f"  ✓ Output saved to: {output_path}")
    except Exception as e:
        print(f"  ✗ Error during CommonRoad to OpenDrive conversion:")
        print(f"    {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Cleanup
    if not keep_temp and temp_path.exists():
        print(f"\n  Removing temporary file: {temp_path}")
        temp_path.unlink()

    print("\n" + "=" * 60)
    print("Conversion completed successfully!")
    print("=" * 60)
    print(f"\nOutput files:")
    if keep_temp:
        print(f"  - CommonRoad XML: {temp_path}")
    print(f"  - OpenDrive XODR: {output_path}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Lanelet2 OSM map to OpenDrive format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.osm
  %(prog)s input.osm output.xodr
  %(prog)s input.osm -o output.xodr
  %(prog)s input.osm -o output.xodr --temp intermediate.xml
  %(prog)s input.osm --no-keep-temp
        """
    )

    parser.add_argument(
        "input",
        type=str,
        help="Path to input Lanelet2 OSM file"
    )

    parser.add_argument(
        "output",
        type=str,
        nargs="?",
        default=None,
        help="Path to output OpenDrive XODR file (default: input file with .xodr extension)"
    )

    parser.add_argument(
        "-o", "--output-file",
        type=str,
        dest="output_alt",
        default=None,
        help="Alternative way to specify output file path"
    )

    parser.add_argument(
        "--temp",
        type=str,
        default=None,
        help="Path to temporary CommonRoad XML file (default: input file with .xml extension)"
    )

    parser.add_argument(
        "--no-keep-temp",
        action="store_true",
        help="Delete temporary CommonRoad XML file after conversion"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Determine input file
    input_osm = args.input

    # Determine output file (prioritize -o flag, then positional arg, then default)
    if args.output_alt:
        output_xodr = args.output_alt
    elif args.output:
        output_xodr = args.output
    else:
        # Default: replace extension with .xodr
        output_xodr = str(Path(input_osm).with_suffix('.xodr'))

    # Determine temp file
    temp_cr = args.temp

    # Determine whether to keep temp file
    keep_temp = not args.no_keep_temp

    # Validate input file exists
    if not Path(input_osm).exists():
        print(f"Error: Input file does not exist: {input_osm}", file=sys.stderr)
        sys.exit(1)

    # Run conversion
    convert_lanelet2_to_opendrive(
        input_osm_path=input_osm,
        output_xodr_path=output_xodr,
        temp_cr_path=temp_cr,
        keep_temp=keep_temp
    )
