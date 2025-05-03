import struct
import yaml
import glob
import os
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

def parse_binary_file(filepath, item_dict, start_index):
    sets = []

    with open(filepath, "rb") as f:
        f.read(24)  # skip offset

        for _ in range(20):
            title_bytes = f.read(16)
            title = title_bytes.decode('ascii', errors='ignore').rstrip('\x00')

            items = []
            for item_index in range(1, 17):  # index: 1 to 16
                storage_id = struct.unpack('B', f.read(1))[0]
                slot_id = struct.unpack('B', f.read(1))[0]
                item_id = struct.unpack('<H', f.read(2))[0]

                item_name = item_dict.get(item_id, item_id)

                items.append({
                    "index": item_index,
                    "storage": storage_id,
                    "slot": slot_id,
                    "item": item_name
                })

            sets.append({
                "index": start_index,
                "title": title,
                "items": items
            })
            start_index += 1

    return sets, start_index

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("-o", "--output", default='eq.yaml')
    parser.add_argument("-i", "--items",
                        default='resources_yaml/data/items.yaml')

    args = parser.parse_args()

    with open(args.items, "r", encoding="utf-8") as f:
        item_dict = yaml.safe_load(f)

    all_sets = []
    index_counter = 1

    for filepath in sorted(glob.glob(os.path.join(args.input_dir, "es*.dat"))):
        sets, index_counter = parse_binary_file(filepath, item_dict, index_counter)
        all_sets.extend(sets)

    jst = ZoneInfo("Asia/Tokyo")
    timestamp = datetime.now(jst).strftime('%Y-%m-%d %H:%M:%S')

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(f"# {timestamp}\n")
        yaml.dump(all_sets, out, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()
