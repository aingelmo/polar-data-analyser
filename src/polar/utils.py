import os
import re


def get_filename_from_response(r) -> str:
    regex = r"filename=\"([\w._-]+)\""
    match = re.search(regex, r.headers["Content-Disposition"])
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not extract filename from Content-Disposition header")


def write_to_file(output_dir: str, filename: str, data: str) -> None:
    outfile = open(os.path.join(output_dir, filename), "w")
    outfile.write(data)
    outfile.close()
