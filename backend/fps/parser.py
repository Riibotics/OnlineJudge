#!/usr/bin/env python3
import base64
import copy
import random
import string
import hashlib
import json
import os
import xml.etree.ElementTree as ET


class FPSParser(object):
    def __init__(self, fps_path=None, string_data=None):
        try:
            if fps_path:
                # Check if file exists and is readable
                if not os.path.exists(fps_path):
                    raise ValueError(f"FPS file not found: {fps_path}")
                
                # Try to read the file content for debugging
                with open(fps_path, 'rb') as f:
                    content = f.read()
                    if len(content) == 0:
                        raise ValueError("FPS file is empty")
                    # Check if it's a ZIP file instead of XML
                    if content[:2] == b'PK':
                        raise ValueError("Uploaded file appears to be a ZIP file. Please extract and upload the fps.xml file directly, or use the correct import method.")
                    # Check for common encoding issues
                    if content[:3] == b'\xef\xbb\xbf':  # UTF-8 BOM
                        content = content[3:]
                
                self._etree = ET.fromstring(content)
            elif string_data:
                self._etree = ET.fromstring(string_data)
            else:
                raise ValueError("You must tell me the file path or directly give me the data for the file")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format in FPS file: {str(e)}")
        except Exception as e:
            if "Invalid XML format" in str(e) or "FPS file" in str(e):
                raise
            raise ValueError(f"Failed to parse FPS file: {str(e)}")
            
        version = self._etree.attrib.get("version", "No Version")
        if version not in ["1.1", "1.2"]:
            raise ValueError("Unsupported version '" + version + "'")

    @property
    def etree(self):
        return self._etree

    def parse(self):
        ret = []
        for node in self._etree:
            if node.tag == "item":
                ret.append(self._parse_one_problem(node))
        return ret

    def _parse_one_problem(self, node):
        sample_start = True
        test_case_start = True
        problem = {"title": "No Title", "description": "No Description",
                   "input": "No Input Description",
                   "output": "No Output Description",
                   "memory_limit": {"unit": None, "value": None},
                   "time_limit": {"unit": None, "value": None},
                   "samples": [], "images": [], "append": [],
                   "template": [], "prepend": [], "test_cases": [],
                   "hint": None, "source": None, "spj": None, "solution": []}
        for item in node:
            tag = item.tag
            if tag in ["title", "description", "input", "output", "hint", "source"]:
                problem[item.tag] = item.text
            elif tag == "time_limit":
                unit = item.attrib.get("unit", "s")
                if unit not in ["s", "ms"]:
                    raise ValueError("Invalid time limit unit")
                problem["time_limit"]["unit"] = item.attrib.get("unit", "s")
                value = int(item.text)
                if value <= 0:
                    raise ValueError("Invalid time limit value")
                problem["time_limit"]["value"] = value
            elif tag == "memory_limit":
                unit = item.attrib.get("unit", "MB")
                if unit not in ["MB", "KB", "mb", "kb"]:
                    raise ValueError("Invalid memory limit unit")
                problem["memory_limit"]["unit"] = unit.upper()
                value = int(item.text)
                if value <= 0:
                    raise ValueError("Invalid memory limit value")
                problem["memory_limit"]["value"] = value
            elif tag in ["template", "append", "prepend", "solution"]:
                lang = item.attrib.get("language")
                if not lang:
                    raise ValueError("Invalid " + tag + ", language name is missed")
                problem[tag].append({"language": lang, "code": item.text})
            elif tag == "spj":
                lang = item.attrib.get("language")
                if not lang:
                    raise ValueError("Invalid spj, language name if missed")
                problem["spj"] = {"language": lang, "code": item.text}
            elif tag == "img":
                problem["images"].append({"src": None, "blob": None})
                for child in item:
                    if child.tag == "src":
                        problem["images"][-1]["src"] = child.text
                    elif child.tag == "base64":
                        problem["images"][-1]["blob"] = base64.b64decode(child.text)
            elif tag == "sample_input":
                if not sample_start:
                    raise ValueError("Invalid xml, error 'sample_input' tag order")
                problem["samples"].append({"input": item.text, "output": None})
                sample_start = False
            elif tag == "sample_output":
                if sample_start:
                    raise ValueError("Invalid xml, error 'sample_output' tag order")
                problem["samples"][-1]["output"] = item.text
                sample_start = True
            elif tag == "test_input":
                if not test_case_start:
                    raise ValueError("Invalid xml, error 'test_input' tag order")
                problem["test_cases"].append({"input": item.text, "output": None})
                test_case_start = False
            elif tag == "test_output":
                if test_case_start:
                    raise ValueError("Invalid xml, error 'test_output' tag order")
                problem["test_cases"][-1]["output"] = item.text
                test_case_start = True

        return problem


class FPSHelper(object):
    def save_image(self, problem, base_dir, base_url):
        _problem = copy.deepcopy(problem)
        for img in _problem["images"]:
            name = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
            ext = os.path.splitext(img["src"])[1]
            file_name = name + ext
            with open(os.path.join(base_dir, file_name), "wb") as f:
                f.write(img["blob"])
            for item in ["description", "input", "output"]:
                _problem[item] = _problem[item].replace(img["src"], os.path.join(base_url, file_name))
        return _problem

    # {
    #     "spj": false,
    #     "test_cases": {
    #         "1": {
    #             "stripped_output_md5": "84f244e41d3c8fd4bdb43ed0e1f7a067",
    #             "input_size": 12,
    #             "output_size": 7,
    #             "input_name": "1.in",
    #             "output_name": "1.out"
    #         }
    #     }
    # }
    def save_test_case(self, problem, base_dir):
        spj = problem.get("spj", {})
        test_cases = {}
        for index, item in enumerate(problem["test_cases"]):
            input_content = item.get("input")
            output_content = item.get("output")
            if input_content:
                with open(os.path.join(base_dir, str(index + 1) + ".in"), "w", encoding="utf-8") as f:
                    f.write(input_content)
            if output_content:
                with open(os.path.join(base_dir, str(index + 1) + ".out"), "w", encoding="utf-8") as f:
                    f.write(output_content)
            if spj:
                one_info = {
                    "input_size": len(input_content),
                    "input_name": f"{index + 1}.in"
                }
            else:
                one_info = {
                    "input_size": len(input_content),
                    "input_name": f"{index + 1}.in",
                    "output_size": len(output_content),
                    "output_name": f"{index + 1}.out",
                    "stripped_output_md5": hashlib.md5(output_content.rstrip().encode("utf-8")).hexdigest()
                }
            test_cases[index] = one_info
        info = {
            "spj": True if spj else False,
            "test_cases": test_cases
        }
        with open(os.path.join(base_dir, "info"), "w", encoding="utf-8") as f:
            f.write(json.dumps(info, indent=4))
        return info


if __name__ == "__main__":
    import pprint

    parser = FPSParser("fps.xml")
    helper = FPSHelper()
    problems = parser.parse()
    for index, problem in enumerate(problems):
        path = os.path.join("/tmp/", str(index + 1))
        os.mkdir(path)
        helper.save_test_case(problem, path)

        pprint.pprint(helper.save_image(problem, "/tmp", "/static/img"))
