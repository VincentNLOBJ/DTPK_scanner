'''
MIT License

Copyright (c) 2023-2024 VincentNL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
# -----------
# HOW-TO-USE
# -----------

Put this script in the same folder of .bin files where you want to search for DTPKs.

'''

import os

class DTPKScan:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.out_dir = os.path.join(dir_path, "DTPK_out")
        self.checkdir()

    def checkdir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def extract(self):
        """Extract DTPK files from .bin files in the given directory."""
        bin_files = [fname for fname in os.listdir(self.dir_path) if fname.endswith(".bin")]

        for fname in bin_files:
            self.process_file(fname)

    def process_file(self, fname):
        """Process an individual .bin file to extract DTPK blocks."""
        file_path = os.path.join(self.dir_path, fname)
        with open(file_path, "rb") as f:
            data = f.read()
            pos = 0
            count = 0
            dtpk_blocks = []

            while pos < len(data):
                pos = data.find(b'DTPK', pos)
                if pos == -1:
                    break

                # Skip if SPSD follows DTPK
                if data[pos + 4:pos + 9].find(b'SPSD') != -1:
                    pos += 8  # Move ahead
                    continue

                # Check for "libintr" at pos + 0x48 (skip if found)
                if pos + 0x49 < len(data) and data[pos + 0x49:pos + 0x49 + 7] == b'libintr':
                    pos += 8  # Move ahead
                    continue

                end_pos = pos + 0x8
                if end_pos + 4 <= len(data):
                    # Read the total DTPK length, starting from 'DTPK'
                    dtpk_len = int.from_bytes(data[end_pos:end_pos + 4], 'little')

                    if dtpk_len > 0 and (pos + dtpk_len) <= len(data):
                        # Extract the DTPK block from pos to pos + dtpk_len
                        dtpk_data = data[pos:pos + dtpk_len]
                        out_fname = os.path.join(self.out_dir, f"{fname[:-4]}_DTPK_{str(count).zfill(3)}.bin")
                        dtpk_blocks.append((out_fname, dtpk_data))  # Add to list for batch writing
                        count += 1

                # Move position forward by the length of the current DTPK block
                pos += max(8, dtpk_len)  # Ensure a minimum forward movement of 8 bytes

            # Write DTPK blocks to files
            self._write_dtpk(dtpk_blocks)

    def _write_dtpk(self, dtpk_blocks):
        """Write DTPKs """
        for out_fname, dtpk_data in dtpk_blocks:
            with open(out_fname, "wb") as out_file:
                out_file.write(dtpk_data)
            print(f"--> {os.path.basename(out_fname)}")

if __name__ == "__main__":

    dir_path = "."
    DTPKScan(dir_path).extract()