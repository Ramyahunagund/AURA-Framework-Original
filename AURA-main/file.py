import ast
import json
import argparse
import subprocess
import shutil
import os
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

# Optional S3 support
try:
    import boto3
except ImportError:
    boto3 = None

SCHEMA_VERSION = "3.0"


# ============================================================
# S3 HELPERS
# ============================================================

def is_s3_path(path: str) -> bool:
    return path.startswith("s3://")


def upload_folder_to_s3(local_dir: Path, s3_uri: str):
    if boto3 is None:
        raise RuntimeError("boto3 not installed")

    print(f"\n☁️ Uploading folder to S3: {s3_uri}")

    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/").rstrip("/")

    s3 = boto3.client("s3")

    for file in local_dir.rglob("*"):
        if file.is_file():
            rel_path = file.relative_to(local_dir)
            key = f"{prefix}/{rel_path}".replace("\\", "/")
            s3.upload_file(str(file), bucket, key)

    print("✅ Upload completed successfully!")


# ============================================================
# GIT CLONE (WINDOWS SAFE)
# ============================================================

def clone_repo(repo_url: str, work_dir: Path):
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)

    print(f"\n📥 Cloning repo: {repo_url}")

    result = subprocess.run(
        ["git", "clone", repo_url, str(work_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        if "Filename too long" in result.stderr or "unable to checkout working tree" in result.stderr:
            print("⚠️ Partial checkout due to Windows long path limits.")
            print("⚠️ Continuing with available files.")
        else:
            print(result.stderr)
            raise RuntimeError("Git clone failed")

    print("✅ Repo cloned successfully (full or partial)")
    return work_dir


# ============================================================
# ROLE CLASSIFICATION
# ============================================================

ROLE_RULES = {
    "TestCase": ["def test_", "pytest", "Test"],
    "Fixture": ["@pytest.fixture"],
    "PageObject": ["Page"],
    "Config": ["yaml", "json", "config", "locale", "profile"],
}


def classify_file_role(path: str, content: str) -> str:
    for role, patterns in ROLE_RULES.items():
        for p in patterns:
            if p in content or p in path:
                return role
    return "Support"


# ============================================================
# SAFE FILE READ
# ============================================================

def safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (FileNotFoundError, OSError):
        return None


# ============================================================
# SYMBOL EXTRACTION
# ============================================================

def extract_symbols(py_file: Path, repo_root: Path):
    txt = safe_read_text(py_file)
    if txt is None:
        return []

    symbols = []
    rel = str(py_file.relative_to(repo_root))

    try:
        tree = ast.parse(txt)
    except:
        return symbols

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            symbols.append({
                "symbol_id": f"{rel}::{node.name}",
                "name": node.name,
                "type": "Function",
                "defined_in": rel,
                "signature": f"({', '.join(args)})"
            })

        elif isinstance(node, ast.ClassDef):
            symbols.append({
                "symbol_id": f"{rel}::{node.name}",
                "name": node.name,
                "type": "Class",
                "defined_in": rel,
                "signature": "()"
            })

    return symbols


# ============================================================
# DIRECT CALL EXTRACTION
# ============================================================

def extract_direct_calls(py_file: Path, repo_root: Path):
    txt = safe_read_text(py_file)
    if txt is None:
        return str(py_file), []

    calls = set()
    rel = str(py_file.relative_to(repo_root))

    try:
        tree = ast.parse(txt)
    except:
        return rel, []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)

    return rel, sorted(calls)


# ============================================================
# FUNCTION INDEX
# ============================================================

def build_function_index(repo_root: Path):
    index = {}

    for f in repo_root.rglob("*.py"):
        txt = safe_read_text(f)
        if txt is None:
            continue

        try:
            tree = ast.parse(txt)
        except:
            continue

        rel = str(f.relative_to(repo_root))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                calls = set()
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        if isinstance(inner.func, ast.Name):
                            calls.add(inner.func.id)
                        elif isinstance(inner.func, ast.Attribute):
                            calls.add(inner.func.attr)

                index[node.name] = {
                    "defined_in": rel,
                    "calls": sorted(calls)
                }

    return index


# ============================================================
# CALL GRAPH HELPERS
# ============================================================

def expand_transitive_calls(direct_calls, function_index):
    visited = set()
    frontier = list(direct_calls)

    while frontier:
        nxt = []
        for f in frontier:
            if f in visited:
                continue
            visited.add(f)
            if f in function_index:
                nxt.extend(function_index[f]["calls"])
        frontier = nxt

    return sorted(visited)


def build_call_tree(func, function_index, depth=5, visited=None):
    if visited is None:
        visited = set()
    if func in visited or depth == 0:
        return {}

    visited.add(func)

    if func not in function_index:
        return {}

    return {
        c: build_call_tree(c, function_index, depth - 1, visited.copy())
        for c in function_index[func]["calls"]
    }


# ============================================================
# STRUCTURE ARTIFACT
# ============================================================

def build_codebase_structure(repo_root: Path):
    inventory = []
    role_counts = defaultdict(int)

    for f in repo_root.rglob("*.py"):
        txt = safe_read_text(f)
        if txt is None:
            continue

        rel = str(f.relative_to(repo_root))
        role = classify_file_role(rel, txt)
        role_counts[role] += 1
        inventory.append({"path": rel, "role": role})

    return {
        "root": repo_root.name,
        "summary": {
            "total_python_files": len(inventory),
            "role_distribution": dict(role_counts)
        },
        "file_inventory": inventory
    }


# ============================================================
# MAIN PACK GENERATION
# ============================================================

def generate_pack(repo_root: Path, output_dir: str, work_dir: Path):
    print("\n🚀 Generating QA Context Pack v3...")

    local_output = Path("_context_pack_output")
    shutil.rmtree(local_output, ignore_errors=True)
    local_output.mkdir()

    py_files = list(repo_root.rglob("*.py"))
    function_index = build_function_index(repo_root)

    symbols, executions = [], []
    reverse_map = defaultdict(list)

    print(f"🔍 Scanning {len(py_files)} Python files...")

    for f in py_files:
        txt = safe_read_text(f)
        if txt is None:
            continue

        rel = str(f.relative_to(repo_root))
        role = classify_file_role(rel, txt)

        symbols.extend(extract_symbols(f, repo_root))
        file_id, direct_calls = extract_direct_calls(f, repo_root)

        if role == "TestCase" or "test" in rel.lower():
            transitive = expand_transitive_calls(direct_calls, function_index)
            tree = {d: build_call_tree(d, function_index) for d in direct_calls}

            executions.append({
                "test_id": file_id,
                "direct_calls": direct_calls,
                "transitive_calls": transitive,
                "execution_tree": tree
            })

            for c in transitive:
                reverse_map[c].append(file_id)

    def write_json(name, data):
        (local_output / name).write_text(json.dumps(data, indent=2))

    write_json("qa_symbols.json", {"schema": SCHEMA_VERSION, "symbols": symbols})
    write_json("qa_execution_graph.json", {"executions": executions})
    write_json("qa_reverse_impact.json", {"reverse_impact": reverse_map})
    write_json("qa_codebase_structure.json", build_codebase_structure(repo_root))

    (local_output / "qa_primitives.md").write_text(
        "\n".join(f"- **{k}**" for k in reverse_map)
    )

    if is_s3_path(output_dir):
        upload_folder_to_s3(local_output, output_dir)
        upload_folder_to_s3(work_dir, f"{output_dir.rstrip('/')}/repo_snapshot")

    print("\n✅ QA Context Pack Generation Complete!")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_url", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--work_dir", default="_cloned_repo")
    args = parser.parse_args()

    repo_root = clone_repo(args.repo_url, Path(args.work_dir))
    generate_pack(repo_root, args.output_dir, Path(args.work_dir))