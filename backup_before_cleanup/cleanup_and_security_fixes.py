#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理和安全修复脚本
清理无关文件，移除硬编码的API密钥，应用安全配置
"""

import os
import re
import shutil
import json
from pathlib import Path
from typing import List, Dict

class ProjectCleanup:
    """项目清理工具"""
    
    def __init__(self, project_root: str = "/Applications/tradingagent"):
        self.project_root = Path(project_root)
        self.files_to_remove = []
        self.files_with_secrets = []
        self.backup_dir = self.project_root / "backup_before_cleanup"
        
    def scan_and_clean(self):
        """扫描并清理项目"""
        print("🔍 开始扫描项目...")
        
        # 1. 扫描无关文件
        self._scan_irrelevant_files()
        
        # 2. 扫描包含API密钥的文件
        self._scan_files_with_secrets()
        
        # 3. 创建备份
        self._create_backup()
        
        # 4. 清理文件
        self._cleanup_files()
        
        # 5. 修复API密钥问题
        self._fix_hardcoded_secrets()
        
        # 6. 生成清理报告
        self._generate_cleanup_report()
        
        print("✅ 项目清理完成!")
        
    def _scan_irrelevant_files(self):
        """扫描无关文件"""
        patterns_to_remove = [
            # 分析报告文件
            "*分析报告*.md",
            "*分析报告*.json", 
            "*分析报告*.txt",
            "*analysis_report*.json",
            "*comprehensive_analysis*.json",
            
            # 中文命名的临时文件
            "*建设工业*.md",
            "*中际旭创*.md",
            "*汇金股份*.md", 
            "*果麦文化*",
            "*铜冠铜箔*.md",
            "*京城股份*.json",
            "*华康洁净*",
            "*淳中科技*.json",
            "*东阳光*.json",
            "*中船应急*.json",
            "*海啸影响*.json",
            "*红旗连锁*.json",
            "*股票分析*.json",
            "*多智能体*.json",
            "*真实数据*",
            "*重启人生*.xlsx",
            
            # 临时数据文件
            "*.log",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            
            # 测试和演示文件
            "demo_*.py",
            "test_*.py",
            "quick_*.py",
            "*_demo.py",
            "*_test.py",
            
            # 特定的单独分析脚本
            "analyze_*.py",
            "huakang_*.py",
            "tibet_*.py",
            "cssc_*.py",
            "seafood_*.py",
            "guomai_*.py",
            "hongqi_*.py",
            "dongyang_*.py",
            
            # 下载的外部代码
            "downloaded_crawlers/",
            
            # 虚拟环境
            "venv_ashare/",
            
            # 备份和压缩文件
            "*.tar.gz",
            "*.zip",
            "*.bak",
            "*.backup",
            
            # CSV数据文件
            "*.csv",
            "*.xlsx",
            "*.xls",
            
            # 因子数据
            "factor_data/",
            "*factor*.json",
            "*factor*.csv",
        ]
        
        for pattern in patterns_to_remove:
            matching_files = list(self.project_root.glob(pattern))
            self.files_to_remove.extend(matching_files)
            
        print(f"📄 找到 {len(self.files_to_remove)} 个待清理文件")
        
    def _scan_files_with_secrets(self):
        """扫描包含API密钥的文件"""
        secret_patterns = [
            r'["\']?[A-Za-z0-9_]*[Tt][Oo][Kk][Ee][Nn]["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'["\']?[A-Za-z0-9_]*[Aa][Pp][Ii][_-]?[Kk][Ee][Yy]["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'sk-[a-zA-Z0-9]+',
            r'tvly-[a-zA-Z0-9-]+',
            r'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065',
        ]
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if file_path.name.startswith('.'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.files_with_secrets.append(file_path)
                        break
                        
            except Exception as e:
                print(f"⚠️ 读取文件失败 {file_path}: {e}")
                
        print(f"🔐 找到 {len(self.files_with_secrets)} 个包含敏感信息的文件")
        
    def _create_backup(self):
        """创建备份"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir()
        
        # 备份包含敏感信息的文件
        for file_path in self.files_with_secrets:
            if file_path.exists():
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                
        print(f"💾 已创建备份目录: {self.backup_dir}")
        
    def _cleanup_files(self):
        """清理文件"""
        removed_count = 0
        
        for file_path in self.files_to_remove:
            if file_path.exists():
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    removed_count += 1
                    print(f"🗑️ 已删除: {file_path.name}")
                except Exception as e:
                    print(f"❌ 删除失败 {file_path}: {e}")
                    
        print(f"🧹 共删除 {removed_count} 个文件/目录")
        
    def _fix_hardcoded_secrets(self):
        """修复硬编码的API密钥"""
        
        # API密钥替换映射
        replacements = {
            # Tushare Token
            r'["\']b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065["\']': 'os.getenv("TUSHARE_TOKEN")',
            r'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065': 'os.getenv("TUSHARE_TOKEN")',
            
            # DashScope API Key
            r'["\']sk-e050041b41674ed7b87644895ebae718["\']': 'os.getenv("DASHSCOPE_API_KEY")',
            r'sk-e050041b41674ed7b87644895ebae718': 'os.getenv("DASHSCOPE_API_KEY")',
            
            # DeepSeek API Key
            r'["\']sk-831cb74319af43ebbfd7ad5e13fd4dfd["\']': 'os.getenv("DEEPSEEK_API_KEY")',
            r'sk-831cb74319af43ebbfd7ad5e13fd4dfd': 'os.getenv("DEEPSEEK_API_KEY")',
            
            # Tavily API Key
            r'["\']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["\']': 'os.getenv("TAVILY_API_KEY")',
            r'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': 'os.getenv("TAVILY_API_KEY")',
        }
        
        fixed_files = []
        
        for file_path in self.files_with_secrets:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 应用所有替换
                for pattern, replacement in replacements.items():
                    content = re.sub(pattern, replacement, content)
                
                # 如果内容有变化，写回文件
                if content != original_content:
                    # 确保文件开头有import os
                    if 'import os' not in content and 'os.getenv' in content:
                        lines = content.split('\n')
                        # 找到第一个import语句的位置
                        import_index = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                import_index = i
                                break
                        
                        lines.insert(import_index, 'import os')
                        content = '\n'.join(lines)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixed_files.append(file_path)
                    print(f"🔧 已修复: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ 修复失败 {file_path}: {e}")
                
        print(f"🔐 共修复 {len(fixed_files)} 个文件的API密钥问题")
        
    def _generate_cleanup_report(self):
        """生成清理报告"""
        report = {
            "cleanup_timestamp": str(datetime.now()),
            "files_removed": [str(f) for f in self.files_to_remove if not f.exists()],
            "files_with_secrets_fixed": [str(f) for f in self.files_with_secrets],
            "backup_location": str(self.backup_dir),
            "summary": {
                "total_files_removed": len([f for f in self.files_to_remove if not f.exists()]),
                "total_secrets_fixed": len(self.files_with_secrets),
                "backup_created": self.backup_dir.exists()
            }
        }
        
        report_file = self.project_root / "CLEANUP_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📋 清理报告已生成: {report_file}")

def create_security_checklist():
    """创建安全检查清单"""
    checklist = """
# 🔒 Trading Agent 安全检查清单

## 部署前必检项目

### 1. 环境变量配置 ✅
- [ ] 复制 `.env.example` 到 `.env`
- [ ] 填入真实的API密钥
- [ ] 确认 `.env` 文件已在 `.gitignore` 中

### 2. 代码安全检查 ✅
- [ ] 所有硬编码API密钥已移除
- [ ] 敏感信息通过环境变量获取
- [ ] 数据库连接字符串已加密

### 3. 文件清理 ✅
- [ ] 删除所有临时分析文件
- [ ] 删除测试和演示脚本
- [ ] 删除个人数据和缓存文件

### 4. 访问控制
- [ ] 设置合适的文件权限
- [ ] 配置防火墙规则
- [ ] 限制API访问频率

### 5. 日志和监控
- [ ] 配置安全日志记录
- [ ] 设置异常监控
- [ ] 启用性能监控

### 6. 备份和恢复
- [ ] 配置定期备份
- [ ] 测试恢复流程
- [ ] 文档化运维流程

## 运行时安全措施

### API密钥管理
- 定期轮换API密钥
- 监控API使用情况
- 设置使用限额

### 数据保护
- 加密敏感数据
- 定期清理临时文件
- 控制数据访问权限

### 系统监控
- 监控系统资源使用
- 跟踪异常请求
- 记录安全事件

## 应急响应

### API密钥泄露
1. 立即撤销泄露的密钥
2. 生成新的密钥
3. 更新系统配置
4. 检查是否有异常访问

### 系统入侵
1. 隔离受影响系统
2. 分析攻击向量
3. 修复安全漏洞
4. 恢复正常服务

### 数据泄露
1. 评估泄露范围
2. 通知相关方
3. 加强安全措施
4. 监控后续影响
"""
    
    checklist_file = Path("/Applications/tradingagent/SECURITY_CHECKLIST.md")
    with open(checklist_file, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print(f"📋 安全检查清单已创建: {checklist_file}")

if __name__ == "__main__":
    from datetime import datetime
    
    print("🚀 开始项目清理和安全修复...")
    
    # 执行清理
    cleanup = ProjectCleanup()
    cleanup.scan_and_clean()
    
    # 创建安全检查清单
    create_security_checklist()
    
    print("\n" + "="*60)
    print("🎉 清理完成！接下来请：")
    print("1. 复制 .env.example 到 .env 并填入真实API密钥")
    print("2. 检查 SECURITY_CHECKLIST.md 确保安全配置")
    print("3. 测试系统功能正常")
    print("4. 提交代码到Git仓库")
    print("="*60)