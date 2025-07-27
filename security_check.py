#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全检查脚本
验证代码的安全性修复效果
"""

import os
import re
import subprocess
import sys
from pathlib import Path

class SecurityChecker:
    """安全检查器"""
    
    def __init__(self):
        self.issues = []
        self.passed_checks = []
    
    def add_issue(self, severity, file, line, description):
        """添加安全问题"""
        self.issues.append({
            'severity': severity,
            'file': file,
            'line': line,
            'description': description
        })
    
    def add_passed(self, check_name):
        """添加通过的检查"""
        self.passed_checks.append(check_name)
    
    def check_file_exists(self, filepath):
        """检查文件是否存在"""
        return os.path.exists(filepath)
    
    def read_file_safe(self, filepath):
        """安全读取文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.add_issue('HIGH', filepath, 0, f"无法读取文件: {e}")
            return None
    
    def check_input_validation(self):
        """检查输入验证"""
        print("🔍 检查输入验证...")
        
        files_to_check = ['get_codename.py', 'install_dependencies.py']
        
        for filepath in files_to_check:
            if not self.check_file_exists(filepath):
                continue
            
            content = self.read_file_safe(filepath)
            if not content:
                continue
            
            # 检查是否有输入验证函数
            if 'validate_stock_query' in content or 'validate_input' in content:
                self.add_passed(f"输入验证 - {filepath}")
            else:
                self.add_issue('HIGH', filepath, 0, "缺少输入验证")
            
            # 检查是否有长度限制
            if 'len(' in content and ('> 50' in content or '> 100' in content):
                self.add_passed(f"长度限制 - {filepath}")
            else:
                self.add_issue('MEDIUM', filepath, 0, "缺少输入长度限制")
    
    def check_url_security(self):
        """检查URL安全性"""
        print("🔍 检查URL安全性...")
        
        filepath = 'get_codename.py'
        if not self.check_file_exists(filepath):
            return
        
        content = self.read_file_safe(filepath)
        if not content:
            return
        
        # 检查URL编码
        if 'quote(' in content:
            self.add_passed("URL编码")
        else:
            self.add_issue('HIGH', filepath, 0, "URL参数未编码，存在注入风险")
        
        # 检查HTTPS使用
        http_count = len(re.findall(r'http://', content))
        https_count = len(re.findall(r'https://', content))
        
        if https_count > http_count:
            self.add_passed("HTTPS使用")
        else:
            self.add_issue('MEDIUM', filepath, 0, "建议使用HTTPS端点")
    
    def check_subprocess_security(self):
        """检查subprocess安全性"""
        print("🔍 检查subprocess安全性...")
        
        files_to_check = ['install_dependencies.py', 'quick_install.py']
        
        for filepath in files_to_check:
            if not self.check_file_exists(filepath):
                continue
            
            content = self.read_file_safe(filepath)
            if not content:
                continue
            
            # 检查shell=True使用
            if 'shell=True' in content:
                self.add_issue('HIGH', filepath, 0, "使用shell=True存在命令注入风险")
            else:
                self.add_passed(f"subprocess安全 - {filepath}")
    
    def check_ssl_verification(self):
        """检查SSL验证"""
        print("🔍 检查SSL验证...")
        
        filepath = 'get_codename.py'
        if not self.check_file_exists(filepath):
            return
        
        content = self.read_file_safe(filepath)
        if not content:
            return
        
        if 'verify = True' in content or 'verify=True' in content:
            self.add_passed("SSL验证")
        else:
            self.add_issue('MEDIUM', filepath, 0, "未启用SSL证书验证")
    
    def check_logging_security(self):
        """检查日志安全性"""
        print("🔍 检查日志安全性...")
        
        filepath = 'get_codename.py'
        if not self.check_file_exists(filepath):
            return
        
        content = self.read_file_safe(filepath)
        if not content:
            return
        
        # 检查敏感信息脱敏
        if 'sanitize_log_data' in content or 'sanitize_data' in content:
            self.add_passed("日志脱敏")
        else:
            self.add_issue('MEDIUM', filepath, 0, "日志可能包含敏感信息")
    
    def check_file_path_security(self):
        """检查文件路径安全性"""
        print("🔍 检查文件路径安全性...")
        
        files_to_check = ['get_codename.py']
        
        for filepath in files_to_check:
            if not self.check_file_exists(filepath):
                continue
            
            content = self.read_file_safe(filepath)
            if not content:
                continue
            
            # 检查相对路径使用
            if '../' in content:
                self.add_issue('HIGH', filepath, 0, "使用相对路径可能存在目录遍历风险")
            else:
                self.add_passed(f"文件路径安全 - {filepath}")
    
    def check_dependency_security(self):
        """检查依赖包安全性"""
        print("🔍 检查依赖包安全性...")
        
        # 检查是否有已知漏洞的包版本
        vulnerable_packages = {
            'requests': ['2.25.0', '2.25.1'],  # 示例
            'flask': ['1.0.0', '1.0.1'],       # 示例
        }
        
        requirements_files = ['requirements.txt', 'requirements-prod.txt']
        
        for req_file in requirements_files:
            if not self.check_file_exists(req_file):
                continue
            
            content = self.read_file_safe(req_file)
            if not content:
                continue
            
            # 检查版本固定
            if '==' in content:
                self.add_passed(f"版本固定 - {req_file}")
            else:
                self.add_issue('LOW', req_file, 0, "建议固定依赖包版本")
    
    def check_error_handling(self):
        """检查错误处理"""
        print("🔍 检查错误处理...")
        
        files_to_check = ['get_codename.py', 'install_dependencies.py']
        
        for filepath in files_to_check:
            if not self.check_file_exists(filepath):
                continue
            
            content = self.read_file_safe(filepath)
            if not content:
                continue
            
            # 检查异常处理
            try_count = len(re.findall(r'try:', content))
            except_count = len(re.findall(r'except', content))
            
            if try_count > 0 and except_count >= try_count:
                self.add_passed(f"异常处理 - {filepath}")
            else:
                self.add_issue('MEDIUM', filepath, 0, "缺少充分的异常处理")
    
    def run_external_security_tools(self):
        """运行外部安全工具"""
        print("🔍 运行外部安全工具...")
        
        tools = [
            {
                'name': 'bandit',
                'command': ['bandit', '-r', '.', '-f', 'json'],
                'description': 'Python安全扫描'
            },
            {
                'name': 'safety',
                'command': ['safety', 'check', '--json'],
                'description': '依赖包漏洞扫描'
            }
        ]
        
        for tool in tools:
            try:
                result = subprocess.run(
                    tool['command'], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.add_passed(f"{tool['name']} 扫描")
                else:
                    self.add_issue('INFO', 'external', 0, 
                                 f"{tool['name']} 发现问题: {result.stdout}")
                    
            except FileNotFoundError:
                print(f"⚠️  {tool['name']} 未安装，跳过扫描")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {tool['name']} 扫描超时")
            except Exception as e:
                print(f"⚠️  {tool['name']} 扫描失败: {e}")
    
    def generate_report(self):
        """生成安全报告"""
        print("\\n" + "="*60)
        print("🔒 安全检查报告")
        print("="*60)
        
        # 统计
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low_issues = [i for i in self.issues if i['severity'] == 'LOW']
        info_issues = [i for i in self.issues if i['severity'] == 'INFO']
        
        print(f"\\n📊 检查统计:")
        print(f"  ✅ 通过检查: {len(self.passed_checks)}")
        print(f"  🔴 高风险问题: {len(high_issues)}")
        print(f"  🟡 中风险问题: {len(medium_issues)}")
        print(f"  🔵 低风险问题: {len(low_issues)}")
        print(f"  ℹ️  信息提示: {len(info_issues)}")
        
        # 通过的检查
        if self.passed_checks:
            print(f"\\n✅ 通过的安全检查:")
            for check in self.passed_checks:
                print(f"  • {check}")
        
        # 安全问题
        if self.issues:
            print(f"\\n⚠️  发现的安全问题:")
            
            for severity in ['HIGH', 'MEDIUM', 'LOW', 'INFO']:
                severity_issues = [i for i in self.issues if i['severity'] == severity]
                if severity_issues:
                    severity_icon = {
                        'HIGH': '🔴',
                        'MEDIUM': '🟡', 
                        'LOW': '🔵',
                        'INFO': 'ℹ️'
                    }[severity]
                    
                    print(f"\\n{severity_icon} {severity} 级别问题:")
                    for issue in severity_issues:
                        print(f"  • {issue['file']}:{issue['line']} - {issue['description']}")
        
        # 安全评分
        total_checks = len(self.passed_checks) + len(self.issues)
        if total_checks > 0:
            score = (len(self.passed_checks) / total_checks) * 100
            
            # 根据高风险问题调整评分
            score -= len(high_issues) * 20
            score -= len(medium_issues) * 10
            score -= len(low_issues) * 5
            score = max(0, score)
            
            print(f"\\n🎯 安全评分: {score:.1f}/100")
            
            if score >= 90:
                print("🎉 安全状态: 优秀")
            elif score >= 80:
                print("✅ 安全状态: 良好")
            elif score >= 70:
                print("⚠️  安全状态: 一般")
            else:
                print("🔴 安全状态: 需要改进")
        
        # 建议
        print(f"\\n💡 安全建议:")
        if high_issues:
            print("  1. 优先修复高风险问题")
        if medium_issues:
            print("  2. 及时处理中风险问题")
        print("  3. 定期运行安全检查")
        print("  4. 保持依赖包更新")
        print("  5. 实施代码审查")
        
        return len(high_issues) == 0 and len(medium_issues) <= 2

def main():
    """主检查函数"""
    print("🔒 开始安全检查...")
    
    checker = SecurityChecker()
    
    # 运行各项检查
    checks = [
        checker.check_input_validation,
        checker.check_url_security,
        checker.check_subprocess_security,
        checker.check_ssl_verification,
        checker.check_logging_security,
        checker.check_file_path_security,
        checker.check_dependency_security,
        checker.check_error_handling,
        # checker.run_external_security_tools,  # 可选，需要安装外部工具
    ]
    
    for check in checks:
        try:
            check()
        except Exception as e:
            print(f"❌ 检查失败: {e}")
    
    # 生成报告
    is_secure = checker.generate_report()
    
    return is_secure

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)