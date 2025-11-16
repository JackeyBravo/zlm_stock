import argparse
import asyncio
from datetime import datetime
from typing import List

from ..db.init_db import init_db
from ..services.ingestor import list_known_codes, sync_quotes_for_codes, sync_stock_master


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准了么 | AKShare 数据同步工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="创建/更新数据库表结构")

    subparsers.add_parser("stocks", help="同步 A 股股票基础信息")

    quotes_parser = subparsers.add_parser("quotes", help="同步指定股票的日线行情")
    quotes_parser.add_argument("--codes", type=str, default="", help="股票代码，逗号分隔；若为空则读取数据库前 N 只")
    quotes_parser.add_argument("--limit", type=int, default=5, help="默认读取数据库中前 N 只股票")
    quotes_parser.add_argument("--start", type=str, required=True, help="开始日期，格式 YYYY-MM-DD")
    quotes_parser.add_argument("--end", type=str, required=True, help="结束日期，格式 YYYY-MM-DD")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.command == "init-db":
        await init_db()
        return
    if args.command == "stocks":
        await sync_stock_master()
        return
    if args.command == "quotes":
        codes: List[str]
        if args.codes:
            codes = [code.strip() for code in args.codes.split(",") if code.strip()]
        else:
            codes = await list_known_codes(limit=args.limit)
        if not codes:
            raise SystemExit("无可用股票代码，请先执行 stocks 同步")
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
        await sync_quotes_for_codes(codes, start, end)
        return


if __name__ == "__main__":
    asyncio.run(main())

