"""
历史管理模块 - 处理用户交互历史的记录、存储和检索
"""

import json
import sqlite3
import csv
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from viby.config import config
from viby.utils.logging import get_logger

# 设置日志记录器
logger = get_logger()


class HistoryManager:
    """历史记录管理器，负责记录、存储和检索用户交互历史"""

    def __init__(self):
        """
        初始化历史管理器

        Args:
            config: 应用配置对象。如果未提供，将使用全局单例配置。
        """
        self.config = config
        self.db_path = self._get_db_path()
        self._init_db()

    def _get_db_path(self) -> Path:
        """
        获取历史数据库的路径

        Returns:
            数据库文件路径
        """
        return self.config.config_dir / "history.db"

    def _init_db(self) -> None:
        """初始化SQLite数据库，创建必要的表"""
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 连接数据库
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 创建历史记录表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                response TEXT,
                metadata TEXT
            )
            """)

            # 创建命令历史表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shell_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                directory TEXT,
                exit_code INTEGER,
                metadata TEXT
            )
            """)

            conn.commit()
            conn.close()
            logger.debug(f"历史数据库初始化成功：{self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"初始化历史数据库失败: {e}")

    def add_interaction(
        self,
        content: str,
        response: Optional[str] = None,
        interaction_type: str = "query",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        添加一个用户交互记录到历史

        Args:
            content: 用户输入内容
            response: AI响应内容（可选）
            interaction_type: 交互类型，默认为"query"
            metadata: 相关元数据，例如使用的模型、工具调用信息等

        Returns:
            新添加记录的ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute(
                """INSERT INTO history (timestamp, type, content, response, metadata) 
                VALUES (?, ?, ?, ?, ?)""",
                (timestamp, interaction_type, content, response, metadata_json),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.debug(f"已添加交互记录，ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            logger.error(f"添加交互记录失败: {e}")
            return -1

    def add_shell_command(
        self,
        command: str,
        directory: Optional[str] = None,
        exit_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        添加一个shell命令到历史

        Args:
            command: 执行的命令
            directory: 执行命令的目录
            exit_code: 命令的退出代码
            metadata: 相关元数据

        Returns:
            新添加记录的ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute(
                """INSERT INTO shell_history (timestamp, command, directory, exit_code, metadata) 
                VALUES (?, ?, ?, ?, ?)""",
                (timestamp, command, directory, exit_code, metadata_json),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.debug(f"已添加Shell命令记录，ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            logger.error(f"添加Shell命令记录失败: {e}")
            return -1

    def get_history(
        self, limit: int = 10, offset: int = 0, search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取交互历史记录

        Args:
            limit: 返回的最大记录数量
            offset: 跳过的记录数量
            search_query: 搜索查询字符串

        Returns:
            历史记录列表
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # 结果作为字典返回
            cursor = conn.cursor()

            query = "SELECT * FROM history"
            params = []

            if search_query:
                query += " WHERE content LIKE ? OR response LIKE ?"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # 转换为字典列表
            results = []
            for row in rows:
                record = dict(row)
                if record["metadata"]:
                    record["metadata"] = json.loads(record["metadata"])
                results.append(record)

            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"获取历史记录失败: {e}")
            return []

    def get_shell_history(
        self, limit: int = 10, offset: int = 0, search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取Shell命令历史记录

        Args:
            limit: 返回的最大记录数量
            offset: 跳过的记录数量
            search_query: 搜索查询字符串

        Returns:
            Shell命令历史记录列表
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # 结果作为字典返回
            cursor = conn.cursor()

            query = "SELECT * FROM shell_history"
            params = []

            if search_query:
                query += " WHERE command LIKE ?"
                params.append(f"%{search_query}%")

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # 转换为字典列表
            results = []
            for row in rows:
                record = dict(row)
                if record["metadata"]:
                    record["metadata"] = json.loads(record["metadata"])
                results.append(record)

            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"获取Shell命令历史记录失败: {e}")
            return []

    def clear_history(self) -> bool:
        """
        清除所有历史记录

        Returns:
            是否成功清除
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 删除交互历史
            cursor.execute("DELETE FROM history")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='history'")
            # 删除Shell命令历史
            cursor.execute("DELETE FROM shell_history")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='shell_history'")

            conn.commit()
            conn.close()
            logger.info("已清除所有历史记录")
            return True
        except sqlite3.Error as e:
            logger.error(f"清除历史记录失败: {e}")
            return False

    def export_history(
        self,
        file_path: str,
        format_type: str = "json",
        history_type: str = "interactions",
    ) -> bool:
        """
        导出历史记录到文件

        Args:
            file_path: 导出文件路径
            format_type: 导出格式，支持 "json", "csv", "yaml"
            history_type: 要导出的历史类型，可以是 "interactions" 或 "shell"

        Returns:
            是否成功导出
        """
        try:
            # 获取所有记录
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if history_type == "interactions":
                cursor.execute("SELECT * FROM history ORDER BY timestamp DESC")
            elif history_type == "shell":
                cursor.execute("SELECT * FROM shell_history ORDER BY timestamp DESC")
            else:
                logger.error(f"不支持的历史类型: {history_type}")
                return False

            rows = cursor.fetchall()
            records = [dict(row) for row in rows]

            # 处理元数据字段
            for record in records:
                if record.get("metadata"):
                    record["metadata"] = json.loads(record["metadata"])

            conn.close()

            # 导出文件
            with open(file_path, "w", encoding="utf-8") as f:
                if format_type == "json":
                    json.dump(records, f, ensure_ascii=False, indent=2)
                elif format_type == "csv":
                    if not records:
                        return True

                    # 准备CSV导出
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()

                    # 将复杂字段转换为字符串
                    for record in records:
                        if isinstance(record.get("metadata"), dict):
                            record["metadata"] = json.dumps(record["metadata"])
                        writer.writerow(record)
                elif format_type == "yaml":
                    yaml.dump(records, f, allow_unicode=True)
                else:
                    logger.error(f"不支持的导出格式: {format_type}")
                    return False

            logger.info(f"历史记录已导出到 {file_path}, 格式: {format_type}")
            return True
        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")
            return False

    def update_interaction(self, record_id: int, new_response: str) -> bool:
        """
        更新交互记录的response字段
        Args:
            record_id: 要更新的记录ID
            new_response: 新的响应内容
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                """UPDATE history SET response=? WHERE id=?""",
                (new_response, record_id),
            )

            conn.commit()
            conn.close()
            logger.debug(f"已更新交互记录，ID: {record_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"更新交互记录失败: {e}")
            return False
