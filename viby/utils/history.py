"""
会话管理模块 - 处理用户交互会话的记录、存储和检索，支持会话(session)管理
"""

import json
import sqlite3
import csv
import yaml
import uuid
import contextlib
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
        """初始化会话管理器"""
        self.config = config
        self.db_path = self._get_db_path()
        self._init_db()

    def _get_db_path(self) -> Path:
        """获取历史数据库的路径"""
        return self.config.config_dir / "history.db"

    @contextlib.contextmanager
    def _db_connection(self):
        """获取数据库连接的上下文管理器"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """初始化SQLite数据库，创建必要的表"""
        try:
            with self._db_connection() as conn:
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

                # 创建历史记录表
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

                # 确保至少有一个活跃会话
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
                active_count = cursor.fetchone()[0]

                if active_count == 0:
                    # 检查是否有任何会话
                    cursor.execute("SELECT COUNT(*) FROM sessions")
                    if cursor.fetchone()[0] == 0:
                        # 创建默认会话
                        self._create_default_session(cursor)
                    else:
                        # 将最近的会话设为活跃
                        cursor.execute(
                            """UPDATE sessions SET is_active = 1 
                            WHERE id = (SELECT id FROM sessions ORDER BY last_used DESC LIMIT 1)"""
                        )

                conn.commit()
                logger.debug(f"会话数据库初始化成功：{self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"初始化会话数据库失败: {e}")

    def _create_default_session(self, cursor):
        """创建默认会话"""
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
        return default_session_id

    def get_active_session_id(self) -> str:
        """获取当前活跃会话的ID"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM sessions WHERE is_active = 1 LIMIT 1")
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    # 如果没有活跃会话，创建一个默认会话
                    return self.create_session("默认会话", "自动创建的默认会话")
        except sqlite3.Error as e:
            logger.error(f"获取活跃会话ID失败: {e}")
            # 紧急情况下创建一个新会话
            return self.create_session("紧急会话", "系统恢复创建的会话")

    def create_session(
        self, name: str = None, description: Optional[str] = None
    ) -> str:
        """创建新的会话，如果名称为空则使用默认名称"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # 如果未提供名称，生成默认名称
                if not name:
                    name = self._generate_default_session_name()

                session_id = str(uuid.uuid4())
                current_time = datetime.now().isoformat()

                # 将所有会话设为非活跃
                cursor.execute("UPDATE sessions SET is_active = 0")

                # 插入新会话
                cursor.execute(
                    """INSERT INTO sessions (id, name, created_at, last_used, description, is_active) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (session_id, name, current_time, current_time, description, 1),
                )

                conn.commit()
                logger.debug(f"已创建新会话: {name}, ID: {session_id}")
                return session_id
        except sqlite3.Error as e:
            logger.error(f"创建会话失败: {e}")
            return ""

    def set_active_session(self, session_id: str) -> bool:
        """设置活跃会话"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # 检查会话是否存在
                cursor.execute(
                    "SELECT COUNT(*) FROM sessions WHERE id = ?", (session_id,)
                )
                if cursor.fetchone()[0] == 0:
                    logger.error(f"会话不存在: {session_id}")
                    return False

                # 更新所有会话状态
                cursor.execute("UPDATE sessions SET is_active = 0")
                cursor.execute(
                    "UPDATE sessions SET is_active = 1, last_used = ? WHERE id = ?",
                    (datetime.now().isoformat(), session_id),
                )

                conn.commit()
                logger.debug(f"已将会话 {session_id} 设为活跃")
                return True
        except sqlite3.Error as e:
            logger.error(f"设置活跃会话失败: {e}")
            return False

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """重命名会话"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE sessions SET name = ? WHERE id = ?", (new_name, session_id)
                )

                affected = cursor.rowcount
                conn.commit()

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
        """删除会话及其历史记录"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # 检查是否是活跃会话
                cursor.execute(
                    "SELECT is_active FROM sessions WHERE id = ?", (session_id,)
                )
                result = cursor.fetchone()

                if not result:
                    logger.error(f"会话不存在: {session_id}")
                    return False

                was_active = result[0] == 1

                # 删除历史记录
                cursor.execute(
                    "DELETE FROM history WHERE session_id = ?", (session_id,)
                )
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
                            "UPDATE sessions SET is_active = 1 WHERE id = ?",
                            (result[0],),
                        )

                conn.commit()
                logger.debug(f"已删除会话: {session_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"删除会话失败: {e}")
            return False

    def get_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话列表"""
        try:
            with self._db_connection() as conn:
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
                return sessions
        except sqlite3.Error as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def add_interaction(
        self,
        content: str,
        response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """添加一个用户交互记录"""
        try:
            with self._db_connection() as conn:
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

                # 准备元数据
                metadata_json = json.dumps(metadata) if metadata else None

                # 插入交互记录
                cursor.execute(
                    """INSERT INTO history (session_id, timestamp, type, content, response, metadata) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        session_id,
                        current_time,
                        "query",  # 使用固定值"query"
                        content,
                        response,
                        metadata_json,
                    ),
                )

                record_id = cursor.lastrowid
                conn.commit()
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
        """获取交互历史记录"""
        try:
            with self._db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 如果未指定会话ID，使用当前活跃会话
                if not session_id:
                    session_id = self.get_active_session_id()

                # 构建查询
                query = """
                    SELECT h.*, s.name as session_name 
                    FROM history h 
                    JOIN sessions s ON h.session_id = s.id 
                    WHERE h.session_id = ?
                """
                params = [session_id]

                # 添加搜索条件
                if search_query:
                    query += " AND (h.content LIKE ? OR h.response LIKE ?)"
                    params.extend([f"%{search_query}%", f"%{search_query}%"])

                # 添加排序和分页
                query += " ORDER BY h.timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # 处理结果
                results = []
                for row in rows:
                    record = dict(row)
                    if record["metadata"]:
                        record["metadata"] = json.loads(record["metadata"])
                    results.append(record)

                return results
        except sqlite3.Error as e:
            logger.error(f"获取历史记录失败: {e}")
            return []

    def clear_history(self, session_id: Optional[str] = None) -> bool:
        """清除指定会话的历史记录，并重置ID自增器"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # 如果未指定会话ID，使用当前活跃会话
                if not session_id:
                    session_id = self.get_active_session_id()

                # 删除指定会话的交互历史
                cursor.execute(
                    "DELETE FROM history WHERE session_id = ?", (session_id,)
                )

                # 重置自增器
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='history'")

                conn.commit()

                logger.info(f"已清除会话 {session_id} 的历史记录并重置ID")
                return True
        except sqlite3.Error as e:
            logger.error(f"清除历史记录失败: {e}")
            return False

    def _generate_default_session_name(self) -> str:
        """生成默认会话名称 (会话+数字)"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                # 获取会话数量作为新会话的编号
                cursor.execute("SELECT COUNT(*) FROM sessions")
                count = cursor.fetchone()[0] + 1
                return f"会话{count}"
        except sqlite3.Error as e:
            logger.error(f"生成默认会话名称失败: {e}")
            # 使用时间戳作为备用名称方案
            return f"会话{datetime.now().strftime('%m%d%H%M')}"

    def export_history(
        self,
        file_path: str,
        format_type: str = "json",
        session_id: Optional[str] = None,
    ) -> bool:
        """导出历史记录到文件"""
        try:
            # 如果未指定会话ID，使用当前活跃会话
            if not session_id:
                session_id = self.get_active_session_id()

            # 获取历史记录
            records = self._get_records_for_export(session_id)

            # 如果没有记录，直接返回成功
            if not records:
                return True

            # 导出文件
            return self._write_export_file(file_path, records, format_type)
        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")
            return False

    def _get_records_for_export(self, session_id: str) -> List[Dict[str, Any]]:
        """获取用于导出的记录"""
        with self._db_connection() as conn:
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

            return records

    def _write_export_file(
        self, file_path: str, records: List[Dict[str, Any]], format_type: str
    ) -> bool:
        """写入导出文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            if format_type == "json":
                json.dump(records, f, ensure_ascii=False, indent=2)
            elif format_type == "csv":
                if not records:
                    return True

                # CSV导出
                writer = csv.DictWriter(f, fieldnames=records[0].keys())
                writer.writeheader()

                # 处理复杂字段
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

    def update_interaction(self, record_id: int, new_response: str) -> bool:
        """更新交互记录的response字段"""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE history SET response=? WHERE id=?""",
                    (new_response, record_id),
                )
                conn.commit()

                logger.debug(f"已更新交互记录，ID: {record_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"更新交互记录失败: {e}")
            return False
