"""
会话管理模块 - 处理用户交互会话的记录、存储和检索，支持会话(session)管理
"""

import json
import sqlite3
import csv
import yaml
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from viby.config import config
from viby.utils.logging import get_logger

# 设置日志记录器
logger = get_logger()


class SessionManager:
    """会话管理器，负责记录、存储和检索用户交互历史，支持会话管理"""

    def __init__(self):
        """
        初始化会话管理器
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

            # 创建会话表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 0
            )
            """)

            # 创建历史记录表(添加session_id字段)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                response TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
            """)

            # 检查是否需要添加session_id列
            cursor.execute("PRAGMA table_info(history)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]

            if "session_id" not in column_names and len(column_names) > 0:
                # 创建默认会话
                default_session_id = str(uuid.uuid4())
                current_time = datetime.now().isoformat()
                cursor.execute(
                    """INSERT INTO sessions (id, name, created_at, last_used, description, is_active) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        default_session_id,
                        "默认会话",
                        current_time,
                        current_time,
                        "自动创建的默认会话",
                        1,
                    ),
                )

                # 添加session_id列并设置默认会话ID
                cursor.execute(
                    "ALTER TABLE history ADD COLUMN session_id TEXT NOT NULL DEFAULT ?",
                    (default_session_id,),
                )
                cursor.execute(
                    "UPDATE history SET session_id = ?", (default_session_id,)
                )

            # 确保至少有一个活跃会话
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
            active_count = cursor.fetchone()[0]

            if active_count == 0:
                # 如果没有活跃会话，创建一个默认会话并设为活跃
                cursor.execute("SELECT COUNT(*) FROM sessions")
                if cursor.fetchone()[0] == 0:
                    # 没有任何会话，创建一个新的默认会话
                    default_session_id = str(uuid.uuid4())
                    current_time = datetime.now().isoformat()
                    cursor.execute(
                        """INSERT INTO sessions (id, name, created_at, last_used, description, is_active) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            default_session_id,
                            "默认会话",
                            current_time,
                            current_time,
                            "自动创建的默认会话",
                            1,
                        ),
                    )
                else:
                    # 有会话但没有活跃会话，将最近的一个设为活跃
                    cursor.execute(
                        """UPDATE sessions SET is_active = 1 
                        WHERE id = (SELECT id FROM sessions ORDER BY last_used DESC LIMIT 1)"""
                    )

            conn.commit()
            conn.close()
            logger.debug(f"会话数据库初始化成功：{self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"初始化会话数据库失败: {e}")

    def get_active_session_id(self) -> str:
        """
        获取当前活跃会话的ID

        Returns:
            活跃会话ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM sessions WHERE is_active = 1 LIMIT 1")
            result = cursor.fetchone()

            conn.close()

            if result:
                return result[0]
            else:
                # 如果没有活跃会话，创建一个默认会话
                return self.create_session("默认会话", "自动创建的默认会话")
        except sqlite3.Error as e:
            logger.error(f"获取活跃会话ID失败: {e}")
            # 紧急情况下创建一个新会话
            return self.create_session("紧急会话", "系统恢复创建的会话")

    def create_session(self, name: str, description: Optional[str] = None) -> str:
        """
        创建新的会话

        Args:
            name: 会话名称
            description: 会话描述

        Returns:
            新创建会话的ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            session_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            # 如果要将新会话设为活跃，先将所有会话设为非活跃
            cursor.execute("UPDATE sessions SET is_active = 0")

            cursor.execute(
                """INSERT INTO sessions (id, name, created_at, last_used, description, is_active) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, name, current_time, current_time, description, 1),
            )

            conn.commit()
            conn.close()

            logger.debug(f"已创建新会话: {name}, ID: {session_id}")
            return session_id
        except sqlite3.Error as e:
            logger.error(f"创建会话失败: {e}")
            return ""

    def set_active_session(self, session_id: str) -> bool:
        """
        设置活跃会话

        Args:
            session_id: 要设为活跃的会话ID

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 检查会话是否存在
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE id = ?", (session_id,))
            if cursor.fetchone()[0] == 0:
                logger.error(f"会话不存在: {session_id}")
                conn.close()
                return False

            # 更新所有会话状态
            cursor.execute("UPDATE sessions SET is_active = 0")
            cursor.execute(
                "UPDATE sessions SET is_active = 1, last_used = ? WHERE id = ?",
                (datetime.now().isoformat(), session_id),
            )

            conn.commit()
            conn.close()

            logger.debug(f"已将会话 {session_id} 设为活跃")
            return True
        except sqlite3.Error as e:
            logger.error(f"设置活跃会话失败: {e}")
            return False

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """
        重命名会话

        Args:
            session_id: 会话ID
            new_name: 新名称

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE sessions SET name = ? WHERE id = ?", (new_name, session_id)
            )

            affected = cursor.rowcount
            conn.commit()
            conn.close()

            if affected > 0:
                logger.debug(f"已将会话 {session_id} 重命名为 {new_name}")
                return True
            else:
                logger.error(f"重命名会话失败，会话不存在: {session_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"重命名会话失败: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话及其历史记录

        Args:
            session_id: 要删除的会话ID

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 检查是否是活跃会话
            cursor.execute("SELECT is_active FROM sessions WHERE id = ?", (session_id,))
            result = cursor.fetchone()

            if not result:
                logger.error(f"会话不存在: {session_id}")
                conn.close()
                return False

            was_active = result[0] == 1

            # 删除历史记录
            cursor.execute("DELETE FROM history WHERE session_id = ?", (session_id,))
            # 删除会话
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

            # 如果删除的是活跃会话，需要重新指定一个活跃会话
            if was_active:
                cursor.execute(
                    "SELECT id FROM sessions ORDER BY last_used DESC LIMIT 1"
                )
                result = cursor.fetchone()
                if result:
                    cursor.execute(
                        "UPDATE sessions SET is_active = 1 WHERE id = ?", (result[0],)
                    )

            conn.commit()
            conn.close()

            logger.debug(f"已删除会话: {session_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话列表

        Returns:
            会话列表
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    s.*, 
                    COUNT(h.id) as interaction_count,
                    MAX(h.timestamp) as last_interaction
                FROM 
                    sessions s
                LEFT JOIN 
                    history h ON s.id = h.session_id
                GROUP BY 
                    s.id
                ORDER BY 
                    s.is_active DESC, s.last_used DESC
            """)

            rows = cursor.fetchall()
            sessions = [dict(row) for row in rows]

            conn.close()
            return sessions
        except sqlite3.Error as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def add_interaction(
        self,
        content: str,
        response: Optional[str] = None,
        interaction_type: str = "query",
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """
        添加一个用户交互记录

        Args:
            content: 用户输入内容
            response: AI响应内容（可选）
            interaction_type: 交互类型，默认为"query"
            metadata: 相关元数据，例如使用的模型、工具调用信息等
            session_id: 会话ID，默认为当前活跃会话

        Returns:
            新添加记录的ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 如果未指定会话ID，使用当前活跃会话
            if not session_id:
                session_id = self.get_active_session_id()

            # 更新会话的最后使用时间
            current_time = datetime.now().isoformat()
            cursor.execute(
                "UPDATE sessions SET last_used = ? WHERE id = ?",
                (current_time, session_id),
            )

            timestamp = current_time
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute(
                """INSERT INTO history (session_id, timestamp, type, content, response, metadata) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    timestamp,
                    interaction_type,
                    content,
                    response,
                    metadata_json,
                ),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.debug(f"已添加交互记录，ID: {record_id}，会话: {session_id}")
            return record_id
        except sqlite3.Error as e:
            logger.error(f"添加交互记录失败: {e}")
            return -1

    def get_history(
        self,
        limit: int = 10,
        offset: int = 0,
        search_query: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取交互历史记录

        Args:
            limit: 返回的最大记录数量
            offset: 跳过的记录数量
            search_query: 搜索查询字符串
            session_id: 会话ID，默认为当前活跃会话

        Returns:
            历史记录列表
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # 结果作为字典返回
            cursor = conn.cursor()

            # 如果未指定会话ID，使用当前活跃会话
            if not session_id:
                session_id = self.get_active_session_id()

            query = "SELECT h.*, s.name as session_name FROM history h JOIN sessions s ON h.session_id = s.id WHERE h.session_id = ?"
            params = [session_id]

            if search_query:
                query += " AND (h.content LIKE ? OR h.response LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            query += " ORDER BY h.timestamp DESC LIMIT ? OFFSET ?"
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

    def clear_history(self, session_id: Optional[str] = None) -> bool:
        """
        清除指定会话的历史记录

        Args:
            session_id: 会话ID，默认为当前活跃会话

        Returns:
            是否成功清除
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 如果未指定会话ID，使用当前活跃会话
            if not session_id:
                session_id = self.get_active_session_id()

            # 删除指定会话的交互历史
            cursor.execute("DELETE FROM history WHERE session_id = ?", (session_id,))

            conn.commit()
            conn.close()
            logger.info(f"已清除会话 {session_id} 的历史记录")
            return True
        except sqlite3.Error as e:
            logger.error(f"清除历史记录失败: {e}")
            return False

    def export_history(
        self,
        file_path: str,
        format_type: str = "json",
        session_id: Optional[str] = None,
    ) -> bool:
        """
        导出历史记录到文件

        Args:
            file_path: 导出文件路径
            format_type: 导出格式，支持 "json", "csv", "yaml"
            session_id: 要导出的会话ID，默认为当前活跃会话

        Returns:
            是否成功导出
        """
        try:
            # 如果未指定会话ID，使用当前活跃会话
            if not session_id:
                session_id = self.get_active_session_id()

            # 获取所有记录
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT h.*, s.name as session_name 
                FROM history h 
                JOIN sessions s ON h.session_id = s.id 
                WHERE h.session_id = ? 
                ORDER BY h.timestamp DESC
            """,
                (session_id,),
            )

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

# 兼容旧代码的别名
HistoryManager = SessionManager
