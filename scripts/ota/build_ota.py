"""
五管 OTA Schematic 构建脚本（Python 入口）
==========================================

本脚本通过 load_il 加载 build_ota.il，在 Virtuoso 内部一次性运行所有
SKILL 操作来构建 OTA_test schematic。

为什么用 .il 文件而不是直接 execute_skill：
  - schCreatePin(cv nil ...) 需要在与 instance/net 创建相同的 SKILL 会话内调用
  - .il 文件中的 procedure 在同一上下文中执行，避免跨调用的状态问题
  - 与项目中 inverter 示例保持一致的模式

使用方法（在项目根目录）：
  uv run python scripts/ota/build_ota.py
"""

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from virtuoso_bridge import VirtuosoClient

LIB  = "test"
CELL = "OTA_test"

# build_ota.il 的本地路径
IL_FILE = Path(__file__).parent / "build_ota.il"


def main():
    with VirtuosoClient.from_env() as client:

        # Step 1：把 .il 文件上传并加载到 Virtuoso
        print(f"加载 {IL_FILE.name} ...")
        client.load_il(str(IL_FILE))
        print("  加载完成。")

        # Step 2：调用 BuildOTA 过程构建 schematic
        print(f"构建 {LIB}/{CELL}/schematic ...")
        result = client.execute_skill(f'BuildOTA("{LIB}" "{CELL}")')
        if result.errors:
            print(f"  错误: {result.errors}")
            return
        print(f"  {result.output}")

        # Step 3：验证结果
        print("\n验证结果 ...")
        client.execute_skill(
            f'setq(_cv dbOpenCellViewByType("{LIB}" "{CELL}" "schematic" "" "r"))'
        )
        inst_count = client.execute_skill("length(_cv~>instances)").output
        net_count  = client.execute_skill("length(_cv~>nets)").output
        term_count = client.execute_skill("length(_cv~>terminals)").output
        terms      = client.execute_skill(
            'let((out) out="" foreach(trm _cv~>terminals out=strcat(out trm->name ":" trm->direction " ")) out)'
        ).output

        print(f"  实例数  : {inst_count}")
        print(f"  net 数  : {net_count}")
        print(f"  端口数  : {term_count}")
        print(f"  端口列表: {terms}")


if __name__ == "__main__":
    main()
