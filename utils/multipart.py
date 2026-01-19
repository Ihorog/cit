import io
from dataclasses import dataclass
from typing import BinaryIO, Dict, Union, Optional

@dataclass
class UploadedFile:
    filename: str
    content_type: str
    data: bytes

def parse_multipart_form(rfile: BinaryIO, headers) -> Dict[str, Union[UploadedFile, str]]:
    content_type = headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        return {}
    
    boundary = content_type.split("boundary=")[-1].encode()
    raw_data = rfile.read(int(headers.get("Content-Length", 0)))
    parts = raw_data.split(b"--" + boundary)
    
    fields = {}
    for part in parts:
        if b"Content-Disposition" not in part: continue
        head, body = part.split(b"\r\n\r\n", 1)
        body = body.rstrip(b"\r\n--\r\n").rstrip(b"\r\n")
        
        head_str = head.decode(errors="ignore")
        name_match = re.search(r'name="([^"]+)"', head_str)
        file_match = re.search(r'filename="([^"]+)"', head_str)
        
        if file_match:
            fields[name_match.group(1)] = UploadedFile(
                filename=file_match.group(1),
                content_type="application/octet-stream",
                data=body
            )
        elif name_match:
            fields[name_match.group(1)] = body.decode(errors="ignore")
    return fields
import re
