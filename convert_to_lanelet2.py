#!/usr/bin/env python3
"""
OpenDRIVE to Lanelet2 Converter
Preserves 3D elevation data throughout the conversion
"""
import sys
from pathlib import Path
from crdesigner.map_conversion.map_conversion_interface import (
    opendrive_to_commonroad,
    commonroad_to_lanelet
)
from crdesigner.common.file_writer import CRDesignerFileWriter
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.scenario.scenario import Tag
from commonroad.common.file_writer import OverwriteExistingFile

def convert(input_file, output_file=None):
    """Convert OpenDRIVE to Lanelet2"""
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Determine output filename
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_lanelet2.osm"
    else:
        output_file = Path(output_file)

    temp_file = input_path.parent / f"{input_path.stem}_temp.xml"

    print(f"Converting: {input_path.name} → {output_file.name}")
    print("-" * 80)

    # Step 1: OpenDRIVE → CommonRoad
    print("[1/3] Converting OpenDRIVE → CommonRoad...")
    scenario = opendrive_to_commonroad(str(input_path))

    num_lanelets = len(scenario.lanelet_network.lanelets)
    print(f"   ✓ Converted {num_lanelets} lanelets")

    # Check for 3D elevation
    if num_lanelets > 0:
        sample = scenario.lanelet_network.lanelets[0]
        if sample.left_vertices.shape[1] == 3:
            elevs = [ll.left_vertices[:, 2] for ll in scenario.lanelet_network.lanelets]
            all_elevs = [e for el in elevs for e in el]
            print(f"   ✓ 3D elevation: {min(all_elevs):.2f}m to {max(all_elevs):.2f}m")

    # Step 2: Save temporary CommonRoad file
    print("[2/3] Saving CommonRoad scenario...")
    writer = CRDesignerFileWriter(
        scenario, PlanningProblemSet(),
        author="Converter", affiliation="CommonRoad",
        source="OpenDRIVE", tags={Tag.URBAN}
    )
    writer.write_to_file(str(temp_file), OverwriteExistingFile.ALWAYS)
    print(f"   ✓ Saved temporary file")

    # Step 3: CommonRoad → Lanelet2
    print("[3/3] Converting CommonRoad → Lanelet2...")
    commonroad_to_lanelet(str(temp_file), str(output_file))

    # Clean up temporary file
    temp_file.unlink()

    # Check output
    size = output_file.stat().st_size
    print(f"   ✓ Created Lanelet2 file ({size:,} bytes)")

    print("-" * 80)
    print(f"✓ SUCCESS: {output_file}")
    print()
    print("View with:")
    print(f"  josm {output_file}")
    print("  (Install JOSM with Lanelet2 plugin)")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_lanelet2.py <input.xodr> [output.osm]")
        print()
        print("Example:")
        print("  python convert_to_lanelet2.py input/Town04.xodr")
        print("  python convert_to_lanelet2.py input/Town04.xodr output/my_map.osm")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert(input_file, output_file)
