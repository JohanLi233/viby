import unittest
import tempfile
from unittest.mock import patch, MagicMock
import requests

from viby.viby_tool_search.client import search_similar_tools
from viby.viby_tool_search.utils import get_mcp_tools_from_cache
from viby.tools.tool_retrieval import execute_tool_retrieval
from viby.viby_tool_search.common import DEFAULT_PORT


class TestToolRetrieval(unittest.TestCase):
    """测试工具检索函数"""

    def setUp(self):
        """测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()

        # 模拟get_text函数，解决本地化管理器未初始化的问题
        patcher = patch("viby.tools.tool_retrieval.get_text")
        self.mock_get_text = patcher.start()
        # 让get_text返回第三个参数（默认文本）或空字符串
        self.mock_get_text.side_effect = (
            lambda group, key, *args: args[0] if args else ""
        )
        self.addCleanup(patcher.stop)

        # 模拟内部函数中的get_text
        patcher2 = patch("viby.locale.get_text")
        self.mock_locale_get_text = patcher2.start()
        self.mock_locale_get_text.side_effect = (
            lambda group, key, *args: args[0] if args else ""
        )
        self.addCleanup(patcher2.stop)

    def tearDown(self):
        """测试后清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_tool_embedding_manager_initialization(self):
        """测试ToolEmbeddingManager的初始化"""
        from viby.viby_tool_search.embedding_manager import EmbeddingManager

        # 模拟Config和logger
        with (
            patch("viby.config.Config") as mock_config,
            patch("viby.viby_tool_search.embedding_manager.logger") as mock_logger,
            patch("viby.locale.get_text") as mock_get_text,
            patch("viby.viby_tool_search.embedding_manager.Path.mkdir"),
        ):
            # 设置mock_logger的level属性为整数，避免TypeError
            mock_logger.level = 0

            # 让get_text返回第三个参数或空字符串
            mock_get_text.side_effect = (
                lambda group, key, *args: args[0] if args else ""
            )

            # 模拟config的get_embedding_config方法
            mock_config_instance = MagicMock()
            mock_config_instance.get_embedding_config.return_value = {}
            mock_config.return_value = mock_config_instance

            # 模拟加载缓存的调用
            with (
                patch(
                    "viby.viby_tool_search.embedding_manager.EmbeddingManager._load_cached_embeddings"
                ) as mock_load_cached,
                patch(
                    "viby.viby_tool_search.embedding_manager.EmbeddingManager._load_model"
                ) as mock_load_model,
            ):
                # 创建管理器并测试期望的行为
                EmbeddingManager()
                mock_load_cached.assert_called_once()
                # 验证没有尝试加载模型
                mock_load_model.assert_not_called()

    @patch("viby.viby_tool_search.utils.get_text")
    def test_collect_mcp_tools(self, mock_get_text):
        """测试工具收集函数"""
        # 让模拟get_text返回空字符串
        mock_get_text.return_value = ""

        # 使用正确的路径模拟Config类
        with patch("viby.config.Config") as mock_config_class:
            # 模拟MCP禁用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = False
            mock_config_class.return_value = mock_config_instance

            # 测试MCP禁用时返回空字典
            result = get_mcp_tools_from_cache()
            self.assertEqual(result, {})

        # 模拟Config和EmbeddingManager
        with (
            patch("viby.config.Config") as mock_config_class,
            patch(
                "viby.viby_tool_search.utils.EmbeddingManager"
            ) as mock_embedding_manager,
        ):
            # 模拟MCP启用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = True
            mock_config_class.return_value = mock_config_instance

            # 模拟EmbeddingManager实例
            mock_manager_instance = MagicMock()
            mock_embedding_manager.return_value = mock_manager_instance

            # 创建模拟工具信息
            mock_tool_info = {
                "tool1": {
                    "definition": {
                        "name": "tool1",
                        "description": "Tool 1 description",
                        "parameters": {"type": "object"},
                        "server_name": "server1",
                    }
                }
            }

            mock_manager_instance.tool_info = mock_tool_info

            # 测试正常收集工具
            result = get_mcp_tools_from_cache()
            self.assertEqual(len(result), 1)
            self.assertIn("server1", result)
            self.assertEqual(len(result["server1"]), 1)
            self.assertEqual(result["server1"][0].name, "tool1")

        # 模拟Config和EmbeddingManager抛出异常
        with (
            patch("viby.config.Config") as mock_config_class,
            patch(
                "viby.viby_tool_search.utils.EmbeddingManager"
            ) as mock_embedding_manager,
            patch("viby.viby_tool_search.utils.logger") as mock_logger,
        ):
            # 模拟MCP启用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = True
            mock_config_class.return_value = mock_config_instance

            # 设置mock_logger的level属性为整数，避免TypeError
            mock_logger.level = 0
            mock_logger.warning = MagicMock()

            # 模拟EmbeddingManager抛出异常
            mock_embedding_manager.side_effect = Exception("测试异常")

            # 测试异常情况
            result = get_mcp_tools_from_cache()
            self.assertEqual(result, {})
            mock_logger.warning.assert_called_once()

    @patch("viby.viby_tool_search.client.is_server_running", return_value=True)
    @patch("viby.viby_tool_search.client.requests")
    @patch("viby.viby_tool_search.client.logger")
    def test_search_tools(self, mock_logger, mock_requests, mock_is_running):
        """测试search_similar_tools函数"""
        # 设置mock_logger的level属性为整数，避免TypeError
        mock_logger.debug = MagicMock()
        mock_logger.error = MagicMock()
        mock_logger.warning = MagicMock()

        # 模拟requests.post的结果
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "name": "test_tool",
                "score": 0.95,
                "definition": {
                    "name": "test_tool",
                    "description": "测试工具",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string", "description": "参数1"}
                        },
                        "required": ["param1"],
                    },
                },
            }
        ]
        mock_requests.post.return_value = mock_response

        # 确保requests.Timeout是BaseException子类的异常
        mock_requests.Timeout = requests.Timeout
        mock_requests.ConnectionError = requests.ConnectionError
        mock_requests.RequestException = requests.RequestException

        # 执行搜索
        results = search_similar_tools("测试查询", top_k=3)

        # 验证结果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test_tool")
        self.assertAlmostEqual(results[0]["score"], 0.95)

        # 验证调用了请求
        mock_requests.post.assert_called_once()
        args, kwargs = mock_requests.post.call_args
        self.assertEqual(args[0], f"http://localhost:{DEFAULT_PORT}/search")
        self.assertEqual(kwargs["json"], {"query": "测试查询", "top_k": 3})

    @patch("viby.tools.tool_retrieval.search_similar_tools")
    def test_execute_tool_retrieval(self, mock_search):
        """测试execute_tool_retrieval函数"""
        # 测试空查询
        result = execute_tool_retrieval({})
        self.assertIn("error", result)

        # 测试空查询
        result = execute_tool_retrieval({"query": ""})
        self.assertIn("error", result)

        # 模拟search_tools在被调用时抛出异常
        mock_search.side_effect = Exception("测试异常")
        with patch("viby.tools.tool_retrieval.logger") as mock_logger:
            # 设置mock_logger的level属性为整数，避免TypeError
            mock_logger.level = 0
            mock_logger.error = MagicMock()

            # 调用函数
            result = execute_tool_retrieval({"query": "测试查询"})

            # 确保返回的是包含错误信息的字典而不是列表
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)

            # 验证记录了错误日志
            mock_logger.error.assert_called()

        # 测试正常情况
        mock_result = [{"name": "test_tool", "score": 0.95}]
        mock_search.side_effect = None
        mock_search.return_value = mock_result

        result = execute_tool_retrieval({"query": "测试查询", "top_k": 2})

        # 验证结果类型和内容
        self.assertIsInstance(result, list)
        self.assertEqual(result, mock_result)
        mock_search.assert_called_with("测试查询", 2)
