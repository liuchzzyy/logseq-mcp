from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from .logseq import LogseqClient
from ..config.settings import settings
from ..server import serve
from ..services.blocks import BlockService
from ..services.graph import GraphService
from ..services.pages import PageService
from ..services.queries import QueryService
from ..models.schemas import (
    AdvancedQueryInput,
    BatchBlockInput,
    CreatePageInput,
    DeleteBlockInput,
    DeletePageInput,
    GetAllPagesInput,
    GetBlockInput,
    GetPageInput,
    GetTasksInput,
    MoveBlockInput,
    RenamePageInput,
    SimpleQueryInput,
    InsertBlockInput,
    UpdateBlockInput,
    EmptyInput,
)


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
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in file {path}: {exc}") from exc


def main() -> None:
    """CLI entrypoint: serve (default) or Logseq operations via subcommands."""

    load_dotenv()

    parser = argparse.ArgumentParser(description="LogSeq MCP CLI")
    parser.add_argument("--api-key", type=str, help="LogSeq API key")
    parser.add_argument("--url", type=str, help="LogSeq API host")

    subparsers = parser.add_subparsers(dest="command")

    # serve
    subparsers.add_parser("serve", help="Run MCP server (default)")

    # pages
    pages = subparsers.add_parser("pages", help="Page operations")
    pages_sub = pages.add_subparsers(dest="action", required=True)

    pages_sub.add_parser("list", help="List all pages").add_argument(
        "--repo", type=str, default=None, help="Repository name (optional)"
    )

    get_page = pages_sub.add_parser("get", help="Get page by name/UUID")
    get_page.add_argument("--name", required=True, help="Page name or UUID")
    get_page.add_argument("--children", action="store_true", help="Include child blocks")

    create_page = pages_sub.add_parser("create", help="Create page")
    create_page.add_argument("--name", required=True, help="Page name")
    create_page.add_argument("--properties", help="JSON object of properties")
    create_page.add_argument("--journal", action="store_true", help="Create as journal")
    create_page.add_argument(
        "--format",
        choices=["markdown", "org"],
        default="markdown",
        help="Page format",
    )
    create_page.add_argument(
        "--create-first-block",
        action="store_true",
        default=False,
        help="Create initial empty block",
    )

    delete_page = pages_sub.add_parser("delete", help="Delete page")
    delete_page.add_argument("--name", required=True, help="Page name")

    rename_page = pages_sub.add_parser("rename", help="Rename page")
    rename_page.add_argument("--old", required=True, help="Current page name")
    rename_page.add_argument("--new", required=True, help="New page name")

    # journals (alias of pages create with journal flag)
    journals = subparsers.add_parser("journals", help="Journal operations")
    journals_sub = journals.add_subparsers(dest="action", required=True)
    journal_create = journals_sub.add_parser("create", help="Create journal page")
    journal_create.add_argument("--name", required=True, help="Journal page name")
    journal_create.add_argument("--properties", help="JSON object of properties")
    journal_list = journals_sub.add_parser("list", help="List pages (all)")
    journal_list.add_argument("--repo", type=str, default=None, help="Repository name (optional)")

    # blocks
    blocks = subparsers.add_parser("blocks", help="Block operations")
    blocks_sub = blocks.add_subparsers(dest="action", required=True)

    blk_get = blocks_sub.add_parser("get", help="Get block by UUID")
    blk_get.add_argument("--uuid", required=True)

    blk_insert = blocks_sub.add_parser("insert", help="Insert block")
    blk_insert.add_argument("--parent", help="Parent block UUID or page name")
    blk_insert.add_argument("--content", required=True, help="Block content")
    blk_insert.add_argument("--as-page-block", action="store_true", help="Insert as page block")
    blk_insert.add_argument("--before", action="store_true", help="Insert before parent")
    blk_insert.add_argument("--custom-uuid", help="Custom UUID")
    blk_insert.add_argument("--properties", help="JSON object of properties")

    blk_update = blocks_sub.add_parser("update", help="Update block")
    blk_update.add_argument("--uuid", required=True)
    blk_update.add_argument("--content", required=True)
    blk_update.add_argument("--properties", help="JSON object of properties")

    blk_delete = blocks_sub.add_parser("delete", help="Delete block")
    blk_delete.add_argument("--uuid", required=True)

    blk_move = blocks_sub.add_parser("move", help="Move block")
    blk_move.add_argument("--uuid", required=True)
    blk_move.add_argument("--target", required=True, help="Target block UUID")
    blk_move.add_argument("--as-child", action="store_true", help="Move as child")

    blk_batch = blocks_sub.add_parser("batch-insert", help="Batch insert blocks from JSON file")
    blk_batch.add_argument("--parent", required=True, help="Parent block or page")
    blk_batch.add_argument("--file", required=True, help="Path to JSON file of blocks list")

    blk_page_blocks = blocks_sub.add_parser("page-blocks", help="Get blocks of a page")
    blk_page_blocks.add_argument("--page", required=True, help="Page name")

    blocks_sub.add_parser("current-page-blocks", help="Get blocks of current page")
    blocks_sub.add_parser("current-block", help="Get currently focused block")

    # queries
    queries = subparsers.add_parser("queries", help="Query operations")
    queries_sub = queries.add_subparsers(dest="action", required=True)

    q_simple = queries_sub.add_parser("simple", help="Simple query")
    q_simple.add_argument("--query", required=True, help="Query string, e.g., [[tag]] or #tag")

    q_adv = queries_sub.add_parser("advanced", help="Advanced datascript query")
    q_adv.add_argument("--query", required=True, help="Datascript query string")
    q_adv.add_argument("--inputs", help="JSON array of inputs", default="[]")

    q_tasks = queries_sub.add_parser("tasks", help="Get tasks")
    q_tasks.add_argument("--marker", help="Marker filter (TODO, DOING, DONE, etc.)")
    q_tasks.add_argument("--priority", help="Priority filter (A, B, C)")

    q_prop = queries_sub.add_parser("blocks-with-prop", help="Blocks with property")
    q_prop.add_argument("--property", required=True, help="Property name")
    q_prop.add_argument("--value", help="Optional value to match")

    # graph
    graph = subparsers.add_parser("graph", help="Graph operations")
    graph_sub = graph.add_subparsers(dest="action", required=True)
    graph_sub.add_parser("info", help="Get current graph info")
    graph_sub.add_parser("user-configs", help="Get user configs")
    graph_sub.add_parser("git-status", help="Get git status")

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
                format="markdown",
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
