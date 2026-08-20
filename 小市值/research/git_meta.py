"""封装 git 命令调用（subprocess），替代自建 hash 方案。

所有命令以仓库根为 cwd；git 输出可能含中文路径，
统一用 -c core.quotepath=false 防止非 ASCII 路径被转义（Windows GBK 控制台场景）。
"""
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败: {result.stderr.strip()}")
    return result.stdout.strip()


def git_commit_hash(root: Path) -> str:
    """当前 HEAD 完整 hash。"""
    return _git(root, "rev-parse", "HEAD")


def git_blob_hash(root: Path, relpath: str) -> str:
    """文件内容指纹（git hash-object），与 commit 解耦。"""
    return _git(root, "hash-object", relpath)


def worktree_clean(root: Path, relpath: str) -> bool:
    """relpath 无未提交改动（含未跟踪文件），返回 True。

    用 porcelain 输出判断：输出为空即干净。
    -c core.quotepath=false 保证中文文件名不被 \345\260\217 形式转义。
    """
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--porcelain", "--", relpath],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout.strip() == ""


def commit_message(root: Path) -> str:
    """最近一次 commit 的 message（change_summary 默认值来源）。"""
    return _git(root, "log", "-1", "--format=%s")


def diff_between(root: Path, h1: str, h2: str, relpath: str) -> str:
    """两个 commit 间指定文件的 diff。"""
    return _git(root, "diff", h1, h2, "--", relpath)