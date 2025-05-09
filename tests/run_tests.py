#!/usr/bin/env python
"""
Viby测试运行器

此脚本提供一个简单的命令行界面来运行Viby测试套件的不同部分。
"""

import argparse
import os
import subprocess
import sys


def run_command(command, title=None):
    """运行一个命令并显示输出"""
    if title:
        separator = "=" * 80
        print(f"\n{separator}")
        print(f" {title} ".center(80, "="))
        print(f"{separator}\n")

    process = subprocess.run(command, shell=True)
    return process.returncode


def run_unit_tests(args):
    """运行单元测试"""
    cmd = f"pytest tests/unit -v {args.pytest_args}"
    if args.coverage:
        cmd += " --cov=viby --cov-report=term --cov-report=xml"
    return run_command(cmd, "运行单元测试")


def run_integration_tests(args):
    """运行集成测试"""
    cmd = f"pytest tests/integration -v {args.pytest_args}"
    if args.coverage:
        cmd += " --cov=viby --cov-report=term --cov-report=xml"
    return run_command(cmd, "运行集成测试")


def run_performance_tests(args):
    """运行性能测试"""
    cmd = f"pytest tests/performance -v {args.pytest_args}"
    return run_command(cmd, "运行性能测试")


def run_e2e_tests(args):
    """运行端到端测试"""
    cmd = f"pytest tests/e2e -v {args.pytest_args}"
    return run_command(cmd, "运行端到端测试")


def run_all_tests(args):
    """运行所有测试"""
    # 先运行单元和集成测试
    unit_result = run_unit_tests(args)
    integration_result = run_integration_tests(args)

    # 如果需要，运行性能测试
    performance_result = 0
    if args.performance:
        performance_result = run_performance_tests(args)

    # 如果需要，运行端到端测试
    e2e_result = 0
    if args.e2e:
        e2e_result = run_e2e_tests(args)

    # 返回总计结果
    return unit_result or integration_result or performance_result or e2e_result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Viby测试运行器")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--e2e", action="store_true", help="运行端到端测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("pytest_args", nargs="*", help="传递给pytest的额外参数")

    args = parser.parse_args()
    args.pytest_args = " ".join(args.pytest_args)

    # 如果没有指定任何测试类型，默认运行单元测试
    if not any([args.unit, args.integration, args.performance, args.e2e, args.all]):
        args.unit = True

    # 设置环境变量以指示测试模式
    os.environ["VIBY_TEST_MODE"] = "1"

    # 运行所选的测试
    if args.all:
        # 默认不包括性能和e2e测试，除非明确指定
        return run_all_tests(args)

    exit_code = 0

    if args.unit:
        unit_result = run_unit_tests(args)
        exit_code = exit_code or unit_result

    if args.integration:
        integration_result = run_integration_tests(args)
        exit_code = exit_code or integration_result

    if args.performance:
        performance_result = run_performance_tests(args)
        exit_code = exit_code or performance_result

    if args.e2e:
        e2e_result = run_e2e_tests(args)
        exit_code = exit_code or e2e_result

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
