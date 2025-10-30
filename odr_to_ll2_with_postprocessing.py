#!/usr/bin/env python3
"""
OpenDRIVE to Lanelet2 conversion with post-processing for VMB format.
Converts XODR files to Lanelet2 OSM format with local coordinates and VMB-specific formatting.
"""
import sys
from pathlib import Path
from lxml import etree

# Direct imports to avoid dependency issues
from crdesigner.map_conversion.opendrive.odr2cr.opendrive_parser.parser import parse_opendrive
from crdesigner.map_conversion.opendrive.odr2cr.opendrive_conversion.network import Network
from crdesigner.common.config.general_config import general_config
from crdesigner.common.config.opendrive_config import open_drive_config
from crdesigner.map_conversion.lanelet2.cr2lanelet import CR2LaneletConverter
from crdesigner.common.config.lanelet2_config import lanelet2_config


def convert_odr_to_ll2_vmb(input_file, output_file=None):
    """
    Convert OpenDRIVE to Lanelet2 with VMB format post-processing.

    Args:
        input_file: Path to input .xodr file
        output_file: Path to output .osm file (optional, auto-generated if not provided)

    Returns:
        Path to the generated output file
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_vmb.osm"
    else:
        output_file = Path(output_file)

    print(f"Converting: {input_path.name} → {output_file.name}")
    print("-" * 80)

    # Step 1: OpenDRIVE → CommonRoad
    print("[1/4] Converting OpenDRIVE → CommonRoad...")
    opendrive = parse_opendrive(input_path)
    road_network = Network()
    road_network.load_opendrive(opendrive)
    scenario = road_network.export_commonroad_scenario(general_config, open_drive_config)

    num_lanelets = len(scenario.lanelet_network.lanelets)
    print(f"   ✓ Converted {num_lanelets} lanelets")

    # Check for 3D elevation
    if num_lanelets > 0:
        sample = scenario.lanelet_network.lanelets[0]
        if sample.left_vertices.shape[1] == 3:
            elevs = [ll.left_vertices[:, 2] for ll in scenario.lanelet_network.lanelets]
            all_elevs = [e for el in elevs for e in el]
            print(f"   ✓ 3D elevation data found!")
            print(f"   ✓ Elevation range: {min(all_elevs):.2f}m to {max(all_elevs):.2f}m")
        else:
            print(f"   ⚠ No elevation data (2D only)")

    # Step 2: CommonRoad → Lanelet2 with local coordinates
    print("[2/4] Converting CommonRoad → Lanelet2 (local coordinates)...")

    # Enable local coordinates
    lanelet2_config.use_local_coordinates = True

    l2osm = CR2LaneletConverter(config=lanelet2_config)
    osm = l2osm(scenario)

    # Step 3: No offset applied - using original coordinates
    print("[3/4] Skipping coordinate offset (using original values)...")
    print(f"   ✓ Using raw coordinates from XODR file")

    # Step 4: Modify to VMB format
    print("[4/4] Applying VMB format...")

    # Change generator to VMB
    osm.set("generator", "VMB")
    # Remove version and upload attributes
    if "version" in osm.attrib:
        del osm.attrib["version"]
    if "upload" in osm.attrib:
        del osm.attrib["upload"]

    # Add MetaInfo element as first child
    metainfo = etree.Element("MetaInfo")
    metainfo.set("format_version", "1")
    metainfo.set("map_version", "2")
    metainfo.set("validation_version", "")
    osm.insert(0, metainfo)

    # Process nodes for VMB format: empty lat/lon and remove extra attributes
    nodes_with_local = 0
    for node in osm.findall('.//node'):
        tags = {tag.get('k'): tag for tag in node.findall('tag')}
        if 'local_x' in tags and 'local_y' in tags:
            # Empty lat/lon for local coordinate nodes
            node.set('lat', '')
            node.set('lon', '')
            nodes_with_local += 1

        # Remove extra attributes for VMB format
        if 'action' in node.attrib:
            del node.attrib['action']
        if 'visible' in node.attrib:
            del node.attrib['visible']
        if 'version' in node.attrib:
            del node.attrib['version']

    # Also clean up way and relation attributes
    for element in osm.findall('.//*[@action]'):
        if 'action' in element.attrib:
            del element.attrib['action']
        if 'visible' in element.attrib:
            del element.attrib['visible']
        if 'version' in element.attrib:
            del element.attrib['version']

    print(f"   ✓ Converted {nodes_with_local} nodes to local coordinates")

    # Write output
    with open(output_file, 'wb') as f:
        f.write(etree.tostring(osm, xml_declaration=True, encoding='UTF-8', pretty_print=True))

    # Check output
    size = output_file.stat().st_size
    print(f"   ✓ Created VMB Lanelet2 file ({size:,} bytes)")

    print("-" * 80)
    print(f"✓ SUCCESS: {output_file}")
    print()
    print("Format:")
    print("  • Generator: VMB")
    print("  • Projection: Local (local_x, local_y)")
    print("  • Elevation: 3D (ele tags)")

    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python odr_to_ll2_with_postprocessing.py <input.xodr> [output.osm]")
        print()
        print("Example:")
        print("  python odr_to_ll2_with_postprocessing.py input/Town04_no_georef.xodr output.osm")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_odr_to_ll2_vmb(input_file, output_file)
