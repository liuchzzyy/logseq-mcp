from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from ..config.settings import settings
from ..models.enums import PageFormat
from ..models.schemas import (
    AdvancedQueryInput,
    BatchBlockInput,
    CreatePageInput,
    DeleteBlockInput,
    DeletePageInput,
    EmptyInput,
    GetAllPagesInput,
    GetBlockInput,
    GetPageInput,
    GetTasksInput,
    InsertBlockInput,
    MoveBlockInput,
    RenamePageInput,
    SimpleQueryInput,
    UpdateBlockInput,
)
from ..server import serve
from ..services.blocks import BlockService
from ..services.graph import GraphService
from ..services.pages import PageService
from ..services.queries import QueryService
from .logseq import LogseqClient


def _load_api_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve API key and URL from CLI args or environment/settings."""
    api_key = args.api_key or os.getenv("LOGSEQ_API_TOKEN") or settings.api_token
    if not api_key:
        raise SystemExit(
            "LogSeq API key must be provided via --api-key or LOGSEQ_API_TOKEN environment variable"
        )

    url = args.url or os.getenv("LOGSEQ_API_URL") or settings.api_url
    if not url:
        raise SystemExit(
            "LogSeq API URL must be provided via --url or LOGSEQ_API_URL environment variable"
        )

    return api_key, url


def _build_services(
    api_key: str, url: str
) -> tuple[BlockService, PageService, QueryService, GraphService]:
    client = LogseqClient(
        base_url=url,
        api_key=api_key,
        timeout=settings.api_timeout,
        max_retries=settings.api_max_retries,
    )
    return (
        BlockService(client),
        PageService(client),
        QueryService(client),
        GraphService(client),
    )


def _to_serializable(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump()
    if isinstance(data, list):
        return [_to_serializable(item) for item in data]
    if isinstance(data, dict):
        return {key: _to_serializable(value) for key, value in data.items()}
    return data


def _print_output(data: Any) -> None:
    """Pretty-print CLI output."""
    if isinstance(data, str):
        print(data)
        return
    print(json.dumps(_to_serializable(data), ensure_ascii=False, indent=2))


def _parse_json(value: str | None, *, field: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for {field}: {exc}") from exc


def _load_json_file(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in file {path}: {exc}") from exc


def main() -> None:
    """CLI entrypoint: serve (default) or Logseq operations via subcommands."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="logseq-mcp",
        description=(
            "Logseq MCP Server & CLI — interact with Logseq graphs via MCP protocol "
            "or command line\n"
            "Logseq MCP 服务器和命令行工具 — 通过 MCP 协议或命令行与 Logseq 图谱交互"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Logseq API authorization token / Logseq API 授权令牌",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Logseq HTTP API URL (default: http://localhost:12315) / Logseq API 地址",
    )

    subparsers = parser.add_subparsers(dest="command")

    # serve
    subparsers.add_parser(
        "serve",
        help="Start MCP server over stdio (default) / 启动 MCP 服务器 (默认)",
    )

    # pages
    pages = subparsers.add_parser(
        "pages",
        help="Manage pages (list/get/create/delete/rename) / 页面管理",
    )
    pages_sub = pages.add_subparsers(dest="action", required=True)

    pages_sub.add_parser(
        "list",
        help="List all pages in the graph / 列出所有页面",
    ).add_argument(
        "--repo",
        type=str,
        default=None,
        help="Repository name (uses current graph if omitted) / 仓库名（省略则使用当前图谱）",
    )

    get_page = pages_sub.add_parser(
        "get", help="Get page details by name or UUID / 按名称或 UUID 获取页面"
    )
    get_page.add_argument("--name", required=True, help="Page name or UUID / 页面名或 UUID")
    get_page.add_argument("--children", action="store_true", help="Include child blocks / 包含子块")

    create_page = pages_sub.add_parser("create", help="Create a new page / 创建新页面")
    create_page.add_argument("--name", required=True, help="Page name / 页面名称")
    create_page.add_argument(
        "--properties",
        help='Page properties as JSON, e.g. \'{"tags":"demo"}\' / 页面属性 (JSON 格式)',
    )
    create_page.add_argument(
        "--journal", action="store_true", help="Create as journal page / 创建为日志页"
    )
    create_page.add_argument(
        "--format",
        choices=["markdown", "org"],
        default="markdown",
        help="Page format (default: markdown) / 页面格式",
    )
    create_page.add_argument(
        "--create-first-block",
        action="store_true",
        default=False,
        help="Create an initial empty block / 创建初始空块",
    )

    delete_page = pages_sub.add_parser("delete", help="Delete a page by name / 按名称删除页面")
    delete_page.add_argument("--name", required=True, help="Page name to delete / 要删除的页面名")

    rename_page = pages_sub.add_parser("rename", help="Rename an existing page / 重命名页面")
    rename_page.add_argument("--old", required=True, help="Current page name / 当前页面名")
    rename_page.add_argument("--new", required=True, help="New page name / 新页面名")

    # journals
    journals = subparsers.add_parser(
        "journals", help="Manage journal pages (create/list) / 日志页管理"
    )
    journals_sub = journals.add_subparsers(dest="action", required=True)
    journal_create = journals_sub.add_parser(
        "create",
        help="Create a journal page for a date / 创建日志页",
    )
    journal_create.add_argument(
        "--name",
        required=True,
        help="Journal date, e.g. '2026-02-07' / 日志日期",
    )
    journal_create.add_argument("--properties", help="Page properties as JSON / 页面属性 (JSON)")
    journal_list = journals_sub.add_parser(
        "list",
        help="List all pages (including journals) / 列出所有页面（含日志）",
    )
    journal_list.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Repository name (uses current graph if omitted) / 仓库名",
    )

    # blocks
    blocks = subparsers.add_parser(
        "blocks",
        help="Manage blocks (get/insert/update/delete/move) / 块管理",
    )
    blocks_sub = blocks.add_subparsers(dest="action", required=True)

    blk_get = blocks_sub.add_parser("get", help="Get block details by UUID / 按 UUID 获取块")
    blk_get.add_argument("--uuid", required=True, help="Block UUID / 块 UUID")

    blk_insert = blocks_sub.add_parser("insert", help="Insert a new block / 插入新块")
    blk_insert.add_argument(
        "--parent",
        help="Parent block UUID or page name (e.g. '[[Page]]') / 父块 UUID 或页面名",
    )
    blk_insert.add_argument("--content", required=True, help="Block content (Markdown) / 块内容")
    blk_insert.add_argument(
        "--as-page-block",
        action="store_true",
        help="Insert as top-level page block / 插入为顶级页面块",
    )
    blk_insert.add_argument(
        "--before",
        action="store_true",
        help="Insert before the parent block / 插入到父块之前",
    )
    blk_insert.add_argument("--custom-uuid", help="Custom UUID for the new block / 自定义 UUID")
    blk_insert.add_argument("--properties", help="Block properties as JSON / 块属性 (JSON)")

    blk_update = blocks_sub.add_parser("update", help="Update block content by UUID / 更新块内容")
    blk_update.add_argument("--uuid", required=True, help="Block UUID to update / 要更新的块 UUID")
    blk_update.add_argument("--content", required=True, help="New block content / 新内容")
    blk_update.add_argument("--properties", help="Updated properties as JSON / 更新属性 (JSON)")

    blk_delete = blocks_sub.add_parser("delete", help="Delete a block by UUID / 删除块")
    blk_delete.add_argument("--uuid", required=True, help="Block UUID to delete / 要删除的块 UUID")

    blk_move = blocks_sub.add_parser("move", help="Move a block to another location / 移动块")
    blk_move.add_argument("--uuid", required=True, help="Block UUID to move / 要移动的块 UUID")
    blk_move.add_argument(
        "--target",
        required=True,
        help="Target block UUID (destination) / 目标块 UUID",
    )
    blk_move.add_argument(
        "--as-child",
        action="store_true",
        help="Move as child of target (default: sibling) / 作为子块移动（默认为同级）",
    )

    blk_batch = blocks_sub.add_parser(
        "batch-insert",
        help="Batch insert blocks from a JSON file / 从 JSON 文件批量插入块",
    )
    blk_batch.add_argument(
        "--parent",
        required=True,
        help="Parent block UUID or page name / 父块 UUID 或页面名",
    )
    blk_batch.add_argument(
        "--file",
        required=True,
        help="Path to JSON file containing blocks array / JSON 文件路径",
    )

    blk_page_blocks = blocks_sub.add_parser(
        "page-blocks",
        help="Get all blocks of a page as tree / 获取页面所有块（树形）",
    )
    blk_page_blocks.add_argument("--page", required=True, help="Page name / 页面名")

    blocks_sub.add_parser(
        "current-page-blocks",
        help="Get all blocks of the active page / 获取当前页面所有块",
    )
    blocks_sub.add_parser(
        "current-block",
        help="Get the currently focused block / 获取当前聚焦块",
    )

    # queries
    queries = subparsers.add_parser(
        "queries",
        help="Query Logseq data (simple/advanced/tasks/properties) / 查询",
    )
    queries_sub = queries.add_subparsers(dest="action", required=True)

    q_simple = queries_sub.add_parser("simple", help="Run a simple Logseq query / 简单查询")
    q_simple.add_argument(
        "--query",
        required=True,
        help="Query string, e.g. '[[tag]]' or '#important' / 查询字符串",
    )

    q_adv = queries_sub.add_parser("advanced", help="Run an advanced DataScript query / 高级查询")
    q_adv.add_argument(
        "--query",
        required=True,
        help="DataScript query, e.g. '[:find (pull ?b [*]) :where ...]' / DataScript 查询语句",
    )
    q_adv.add_argument(
        "--inputs",
        help="Query input parameters as JSON array / 查询参数 (JSON 数组)",
        default="[]",
    )

    q_tasks = queries_sub.add_parser(
        "tasks",
        help="Get tasks, optionally filtered / 获取任务（可按状态/优先级过滤）",
    )
    q_tasks.add_argument(
        "--marker",
        help="Filter: TODO, DOING, DONE, NOW, LATER, WAITING, CANCELLED / 状态过滤",
    )
    q_tasks.add_argument(
        "--priority",
        help="Filter: A (high), B (medium), C (low) / 优先级过滤",
    )

    q_prop = queries_sub.add_parser(
        "blocks-with-prop",
        help="Find blocks with a specific property / 按属性查找块",
    )
    q_prop.add_argument("--property", required=True, help="Property name / 属性名")
    q_prop.add_argument("--value", help="Optional property value to match / 属性值（可选）")

    # graph
    graph = subparsers.add_parser(
        "graph",
        help="Graph & Git operations (info/configs/git-status) / 图谱与 Git 操作",
    )
    graph_sub = graph.add_subparsers(dest="action", required=True)
    graph_sub.add_parser("info", help="Get current graph name, path, and URL / 获取图谱信息")
    graph_sub.add_parser("user-configs", help="Get Logseq user preferences / 获取用户配置")
    graph_sub.add_parser("git-status", help="Get git status of the graph / 获取 Git 状态")

    args = parser.parse_args()

    # Default to serve if no subcommand
    if args.command is None:
        args.command = "serve"

    api_key, url = _load_api_credentials(args)

    if args.command == "serve":
        asyncio.run(serve())
        return

    # Build services once for other commands
    block_service, page_service, query_service, graph_service = _build_services(api_key, url)

    def run(coro):
        return asyncio.run(coro)

    if args.command == "pages":
        action = args.action
        if action == "list":
            result = run(page_service.get_all(GetAllPagesInput(repo=args.repo)))
            _print_output(result)
        elif action == "get":
            result = run(
                page_service.get(
                    GetPageInput(page_name=args.name, include_children=bool(args.children))
                )
            )
            _print_output(result)
        elif action == "create":
            properties = _parse_json(args.properties, field="properties") or {}
            input_data = CreatePageInput(
                page_name=args.name,
                properties=properties,
                journal=bool(args.journal),
                format=args.format,
                create_first_block=bool(args.create_first_block),
            )
            result = run(page_service.create(input_data))
            _print_output(result)
        elif action == "delete":
            result = run(page_service.delete(DeletePageInput(page_name=args.name)))
            _print_output(result)
        elif action == "rename":
            result = run(page_service.rename(RenamePageInput(old_name=args.old, new_name=args.new)))
            _print_output(result)
        return

    if args.command == "journals":
        action = args.action
        if action == "create":
            properties = _parse_json(args.properties, field="properties") or {}
            input_data = CreatePageInput(
                page_name=args.name,
                properties=properties,
                journal=True,
                format=PageFormat.MARKDOWN,
                create_first_block=True,
            )
            result = run(page_service.create(input_data))
            _print_output(result)
        elif action == "list":
            result = run(page_service.get_all(GetAllPagesInput(repo=args.repo)))
            _print_output(result)
        return

    if args.command == "blocks":
        action = args.action
        if action == "get":
            result = run(block_service.get(GetBlockInput(uuid=args.uuid)))
            _print_output(result)
        elif action == "insert":
            properties = _parse_json(args.properties, field="properties")
            input_data = InsertBlockInput(
                parent_block=args.parent,
                content=args.content,
                is_page_block=bool(args.as_page_block),
                before=bool(args.before),
                custom_uuid=args.custom_uuid,
                properties=properties,
            )
            result = run(block_service.insert(input_data))
            _print_output(result)
        elif action == "update":
            properties = _parse_json(args.properties, field="properties")
            input_data = UpdateBlockInput(
                uuid=args.uuid, content=args.content, properties=properties
            )
            result = run(block_service.update(input_data))
            _print_output(result)
        elif action == "delete":
            result = run(block_service.delete(DeleteBlockInput(uuid=args.uuid)))
            _print_output(result)
        elif action == "move":
            input_data = MoveBlockInput(
                uuid=args.uuid, target_uuid=args.target, as_child=bool(args.as_child)
            )
            result = run(block_service.move(input_data))
            _print_output(result)
        elif action == "batch-insert":
            blocks_payload = _load_json_file(args.file)
            if not isinstance(blocks_payload, list):
                raise SystemExit("Batch insert file must contain a JSON array of blocks")
            input_data = BatchBlockInput(parent=args.parent, blocks=blocks_payload)
            result = run(block_service.insert_batch(input_data))
            _print_output(result)
        elif action == "page-blocks":
            result = run(block_service.get_page_blocks(args.page))
            _print_output(result)
        elif action == "current-page-blocks":
            result = run(block_service.get_current_page_blocks())
            _print_output(result)
        elif action == "current-block":
            result = run(block_service.get_current_block())
            _print_output(result)
        return

    if args.command == "queries":
        action = args.action
        if action == "simple":
            result = run(query_service.simple_query(SimpleQueryInput(query=args.query)))
            _print_output(result)
        elif action == "advanced":
            inputs = _parse_json(args.inputs, field="inputs") or []
            if not isinstance(inputs, list):
                raise SystemExit("--inputs must be a JSON array")
            result = run(
                query_service.advanced_query(AdvancedQueryInput(query=args.query, inputs=inputs))
            )
            _print_output(result)
        elif action == "tasks":
            result = run(
                query_service.get_tasks(GetTasksInput(marker=args.marker, priority=args.priority))
            )
            _print_output(result)
        elif action == "blocks-with-prop":
            result = run(query_service.get_blocks_with_property(args.property, args.value))
            _print_output(result)
        return

    if args.command == "graph":
        action = args.action
        if action == "info":
            result = run(graph_service.get_current_graph(EmptyInput()))
            _print_output(result)
        elif action == "user-configs":
            result = run(graph_service.get_user_configs(EmptyInput()))
            _print_output(result)
        elif action == "git-status":
            result = run(graph_service.git_status(EmptyInput()))
            _print_output(result)
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
