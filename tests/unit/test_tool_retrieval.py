"""
工具检索功能的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import tempfile
import shutil
from pathlib import Path

from viby.tools.embedding_utils import ToolEmbeddingManager
from viby.tools.tool_retrieval import search_tools, execute_tool_retrieval


class TestToolRetrieval(unittest.TestCase):
    """测试工具检索功能"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)

    @patch('viby.tools.embedding_utils.ToolEmbeddingManager._load_model')
    def test_tool_embedding_manager_initialization(self, mock_load_model):
        """测试ToolEmbeddingManager初始化"""
        manager = ToolEmbeddingManager(cache_dir=self.temp_dir)
        
        # 验证缓存目录创建
        self.assertTrue(Path(self.temp_dir).exists())
        
        # 验证embedding和工具信息初始化为空字典
        self.assertEqual(manager.tool_embeddings, {})
        self.assertEqual(manager.tool_info, {})
        
        # 验证延迟加载模型机制
        mock_load_model.assert_not_called()

    # 通过直接模拟search_similar_tools来测试search_tools函数
    @patch('viby.tools.tool_retrieval.get_embedding_manager')
    def test_search_tools(self, mock_get_manager):
        """测试search_tools函数"""
        # 创建模拟的manager
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
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
                            "param1": {
                                "type": "string",
                                "description": "参数1"
                            }
                        },
                        "required": ["param1"]
                    }
                }
            }
        ]
        
        # 模拟AVAILABLE_TOOLS的导入
        with patch('viby.tools.tool_retrieval.AVAILABLE_TOOLS', {'test_tool': {}}, create=True):
            results = search_tools("测试查询", top_k=3)
        
        # 验证结果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test_tool")
        self.assertAlmostEqual(results[0]["score"], 0.95)
        
        # 验证调用了update_tool_embeddings和search_similar_tools
        mock_manager.update_tool_embeddings.assert_called_once()
        mock_manager.search_similar_tools.assert_called_once_with("测试查询", 3)

    @patch('viby.tools.tool_retrieval.search_tools')
    def test_execute_tool_retrieval(self, mock_search):
        """测试execute_tool_retrieval函数"""
        # 测试空查询
        result = execute_tool_retrieval({})
        self.assertIn("error", result)
        
        # 测试空查询
        result = execute_tool_retrieval({"query": ""})
        self.assertIn("error", result)
        
        # 测试带查询但search_tools失败
        mock_search.side_effect = Exception("测试异常")
        result = execute_tool_retrieval({"query": "测试查询"})
        self.assertIn("error", result)
        
        # 测试正常查询
        mock_search.side_effect = None
        mock_search.return_value = [
            {
                "name": "test_tool",
                "score": 0.95,
                "definition": {
                    "name": "test_tool",
                    "description": "测试工具",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {
                                "type": "string",
                                "description": "参数1"
                            }
                        },
                        "required": ["param1"]
                    }
                }
            }
        ]
        
        result = execute_tool_retrieval({"query": "测试查询", "top_k": 3})
        
        # 验证结果
        self.assertIn("tools", result)
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(result["tools"][0]["name"], "test_tool")
        self.assertEqual(result["query"], "测试查询")
        self.assertEqual(result["total"], 1)


if __name__ == "__main__":
    unittest.main() 