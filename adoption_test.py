# Copyright 2026 Cloud-Dog, Viewdeck Engineering Limited
# Licensed under the Apache License, Version 2.0
"""
Adoption test for cloud_dog_llm (PS-50).
Run check_adoption(project_root) to verify a project fully uses cloud_dog_llm.
"""
import pathlib
import subprocess


def _grep(pattern: str, search_path: pathlib.Path, extra_flags: str = "") -> list[str]:
    cmd = f"grep -rn {extra_flags} '{pattern}' {search_path} --include='*.py' | grep -v __pycache__ | grep -v '/archive/' | grep -v '/working/'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return [l for l in result.stdout.strip().split('\n') if l]


def _find_source_dirs(project_root: pathlib.Path) -> list[pathlib.Path]:
    dirs = []
    src = project_root / "src"
    if src.is_dir():
        dirs.append(src)
    crawler = project_root / "crawler"
    if crawler.is_dir():
        dirs.append(crawler)
    return dirs


def check_adoption(project_root: pathlib.Path) -> dict:
    results = {"pass": [], "fail": []}
    source_dirs = _find_source_dirs(project_root)

    if not source_dirs:
        results["fail"].append(f"No source directory found in {project_root}")
        return results

    # 1. cloud_dog_llm imported
    all_imports = []
    for sd in source_dirs:
        all_imports.extend(_grep("cloud_dog_llm", sd))
    for f in project_root.glob("start_*.py"):
        cmd = f"grep -n 'cloud_dog_llm' {f}"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.stdout.strip():
            all_imports.extend(r.stdout.strip().split('\n'))
    if len(all_imports) > 0:
        results["pass"].append(f"cloud_dog_llm imported ({len(all_imports)} references)")
    else:
        results["fail"].append("cloud_dog_llm NOT imported anywhere in source")

    # 2. No direct httpx/requests calls to LLM endpoints
    direct_llm_calls = []
    for sd in source_dirs:
        hits = _grep("httpx.post\\|httpx.AsyncClient\\|requests.post", sd)
        for h in hits:
            # Check if it's targeting an LLM endpoint
            filepath = h.split(":")[0]
            line = h.split(":", 2)[-1] if len(h.split(":", 2)) > 2 else ""
            if any(kw in line.lower() for kw in ["ollama", "openai", "anthropic", "openrouter", "v1/chat", "v1/completions", "api/generate"]):
                direct_llm_calls.append(h)
    if len(direct_llm_calls) == 0:
        results["pass"].append("No direct httpx/requests calls to LLM endpoints")
    else:
        results["fail"].append(f"Direct LLM endpoint calls found (should use cloud_dog_llm): {direct_llm_calls}")

    # 3. LLM provider configuration via cloud_dog_llm (LLMClient or get_llm_client)
    client_refs = []
    for sd in source_dirs:
        client_refs.extend(_grep("LLMClient\\|get_llm_client\\|LLMRequest\\|LLMResponse", sd))
    if len(client_refs) > 0:
        results["pass"].append(f"cloud_dog_llm client API used ({len(client_refs)} references)")
    else:
        results["fail"].append("No cloud_dog_llm client API usage (LLMClient/get_llm_client)")

    return results
