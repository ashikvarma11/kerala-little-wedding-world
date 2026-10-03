"""Package the CC0 Quaternius Suit character without its pistol prop.
Usage: python scripts/prepare_modern_character.py work/quaternius-suit.gltf
All original joint animation clips are retained without procedural retargeting.
"""
import base64
import json
from pathlib import Path
import struct
import sys

document = json.loads(Path(sys.argv[1]).read_text())
for node in document['nodes']:
    if node.get('name') == 'Pistol':
        node.pop('mesh', None)
        node.pop('skin', None)
buffer = document['buffers'][0]
binary = base64.b64decode(buffer.pop('uri').split(',', 1)[1])
header = json.dumps(document, separators=(',', ':')).encode()
header += b' ' * (-len(header) % 4)
binary += b'\0' * (-len(binary) % 4)
output = Path(__file__).resolve().parents[1] / 'dist/assets/quaternius-modern-man.glb'
output.write_bytes(struct.pack('<III', 0x46546C67, 2, 28 + len(header) + len(binary))
    + struct.pack('<II', len(header), 0x4E4F534A) + header
    + struct.pack('<II', len(binary), 0x004E4942) + binary)
print(f'{output}: {output.stat().st_size} bytes; {len(document["animations"])} clips')
