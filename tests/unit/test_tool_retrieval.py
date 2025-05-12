import unittest
import tempfile
from unittest.mock import patch, MagicMock

from viby.tools.tool_retrieval import (
    search_tools,
    execute_tool_retrieval,
    execute_update_embeddings,
    collect_mcp_tools,
)


class TestToolRetrieval(unittest.TestCase):
    """测试工具检索函数"""

    def setUp(self):
        """测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟get_text函数，解决本地化管理器未初始化的问题
        patcher = patch("viby.tools.tool_retrieval.get_text")
        self.mock_get_text = patcher.start()
        # 让get_text返回第三个参数（默认文本）或空字符串
        self.mock_get_text.side_effect = lambda group, key, *args: args[0] if args else ""
        self.addCleanup(patcher.stop)
        
        # 模拟内部函数中的get_text
        patcher2 = patch("viby.locale.get_text")
        self.mock_locale_get_text = patcher2.start()
        self.mock_locale_get_text.side_effect = lambda group, key, *args: args[0] if args else ""
        self.addCleanup(patcher2.stop)

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_tool_embedding_manager_initialization(self):
        """测试ToolEmbeddingManager的初始化"""
        from viby.tools.embedding_utils import ToolEmbeddingManager

        # 模拟Config和logger
        with patch("viby.config.Config") as mock_config, patch(
            "viby.tools.embedding_utils.logger"
        ) as mock_logger, patch(
            "viby.locale.get_text"
        ) as mock_get_text, patch(
            "viby.tools.embedding_utils.Path.mkdir"
        ):
            # 让get_text返回第三个参数或空字符串
            mock_get_text.side_effect = lambda group, key, *args: args[0] if args else ""
            
            # 模拟config的get_embedding_config方法
            mock_config_instance = MagicMock()
            mock_config_instance.get_embedding_config.return_value = {}
            mock_config.return_value = mock_config_instance

            # 模拟加载缓存的调用
            with patch(
                "viby.tools.embedding_utils.ToolEmbeddingManager._load_cached_embeddings"
            ) as mock_load_cached, patch(
                "viby.tools.embedding_utils.ToolEmbeddingManager._load_model"
            ) as mock_load_model:
                manager = ToolEmbeddingManager()
                mock_load_cached.assert_called_once()
                # 验证没有尝试加载模型
                mock_load_model.assert_not_called()

    def test_collect_mcp_tools(self):
        """测试collect_mcp_tools函数"""
        # 使用正确的路径模拟Config类
        with patch("viby.config.Config") as mock_config_class:
            # 模拟MCP禁用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = False
            mock_config_class.return_value = mock_config_instance

            # 测试MCP禁用时返回空字典
            result = collect_mcp_tools()
            self.assertEqual(result, {})

        # 模拟Config和list_tools
        with patch("viby.config.Config") as mock_config_class, patch(
            "viby.mcp.list_tools"
        ) as mock_list_tools:
            # 模拟MCP启用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = True
            mock_config_class.return_value = mock_config_instance

            # 创建具有固定name属性的模拟工具
            mock_tool = MagicMock()
            mock_tool.name = "tool1"  # 使用字符串而不是MagicMock对象
            mock_tool.description = "Tool 1 description"
            mock_tool.inputSchema = {"type": "object"}

            # 模拟list_tools返回值
            mock_list_tools.return_value = {
                "server1": [mock_tool]
            }

            # 测试正常收集工具
            result = collect_mcp_tools()
            self.assertEqual(len(result), 1)
            self.assertIn("tool1", result)
            self.assertEqual(result["tool1"]["server_name"], "server1")

        # 模拟Config和list_tools抛出异常
        with patch("viby.config.Config") as mock_config_class, patch(
            "viby.mcp.list_tools"
        ) as mock_list_tools, patch(
            "viby.tools.tool_retrieval.logger"
        ) as mock_logger:
            # 模拟MCP启用
            mock_config_instance = MagicMock()
            mock_config_instance.enable_mcp = True
            mock_config_class.return_value = mock_config_instance

            # 模拟list_tools抛出异常
            mock_list_tools.side_effect = Exception("测试异常")
            mock_logger.error = MagicMock()

            # 测试异常情况
            result = collect_mcp_tools()
            self.assertEqual(result, {})
            mock_logger.error.assert_called_once()

    @patch("viby.tools.tool_retrieval.get_embedding_manager")
    def test_search_tools(self, mock_get_manager):
        """测试search_tools函数"""
        # 创建模拟的manager
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        # 模拟tool_embeddings属性
        mock_manager.tool_embeddings = {"test_tool": [0.1, 0.2, 0.3]}

        # 模拟search_similar_tools返回值
        mock_manager.search_similar_tools.return_value = [
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

        # 执行搜索
        results = search_tools("测试查询", top_k=3)

        # 验证结果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test_tool")
        self.assertAlmostEqual(results[0]["score"], 0.95)

        # 验证调用了search_similar_tools方法
        mock_manager.search_similar_tools.assert_called_once_with("测试查询", 3)

    @patch("viby.tools.tool_retrieval.search_tools")
    def test_execute_tool_retrieval(self, mock_search):
        """测试execute_tool_retrieval函数"""
        # 测试空查询
        result = execute_tool_retrieval({})
        self.assertIn("error", result)

        # 测试空查询
        result = execute_tool_retrieval({"query": ""})
        self.assertIn("error", result)

        # 测试带查询但search_tools失败
        with patch("viby.tools.tool_retrieval.logger") as mock_logger:
            mock_search.side_effect = Exception("测试异常")
            result = execute_tool_retrieval({"query": "测试查询"})
            self.assertIn("error", result)
            # 验证记录了错误日志
            mock_logger.error.assert_called()

        # 测试正常情况
        mock_search.side_effect = None
        mock_search.return_value = [{"name": "test_tool", "score": 0.95}]
        result = execute_tool_retrieval({"query": "测试查询", "top_k": 2})
        self.assertEqual(result, [{"name": "test_tool", "score": 0.95}])
        mock_search.assert_called_with("测试查询", 2)

    @patch("viby.tools.tool_retrieval.collect_mcp_tools")
    @patch("viby.tools.tool_retrieval.get_embedding_manager")
    def test_execute_update_embeddings(self, mock_get_manager, mock_collect_tools):
        """测试execute_update_embeddings函数"""
        # 测试没有工具的情况
        mock_collect_tools.return_value = {}
        result = execute_update_embeddings({})
        self.assertFalse(result["success"])
        self.assertIn("message", result)

        # 测试有工具但更新失败的情况
        mock_collect_tools.return_value = {"tool1": {}, "tool2": {}}
        mock_manager = MagicMock()
        mock_manager.update_tool_embeddings.return_value = False
        mock_get_manager.return_value = mock_manager
        result = execute_update_embeddings({})
        self.assertFalse(result["success"])
        self.assertIn("message", result)
        mock_manager.update_tool_embeddings.assert_called_once_with(
            {"tool1": {}, "tool2": {}}
        )

        # 测试成功更新的情况
        mock_manager.update_tool_embeddings.return_value = True
        result = execute_update_embeddings({})
        self.assertTrue(result["success"])
        self.assertIn("message", result)
        self.assertEqual(result["tool_count"], 2)

        # 测试异常情况 - 使用额外的logger模拟
        with patch("viby.tools.tool_retrieval.logger") as mock_logger:
            mock_manager.update_tool_embeddings.side_effect = Exception("测试异常")
            result = execute_update_embeddings({})
            self.assertFalse(result["success"])
            self.assertIn("error", result)
            mock_logger.error.assert_called_once() 