import os
import struct
import zlib

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


def write_png(path: str, width: int, height: int, red: int, green: int, blue: int) -> None:
    """Записывает одноцветный PNG-файл."""
    def make_chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw_rows = []
    pixel = bytes([red, green, blue])
    for _ in range(height):
        raw_rows.append(b"\x00" + pixel * width)
    compressed = zlib.compress(b"".join(raw_rows), 9)

    png_bytes = b"\x89PNG\r\n\x1a\n"
    png_bytes += make_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png_bytes += make_chunk(b"IDAT", compressed)
    png_bytes += make_chunk(b"IEND", b"")

    with open(path, "wb") as file:
        file.write(png_bytes)


if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)
    write_png(os.path.join(IMAGES_DIR, "background.png"), 32, 32, 100, 180, 100)
    write_png(os.path.join(IMAGES_DIR, "coin.png"), 32, 32, 255, 215, 0)
    print("Images created (cat sprites: use walk_*/wait_* folders)")
