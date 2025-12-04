#!/usr/bin/env python3
"""
DNS解析学习 - 模拟域名解析过程
"""

import socket

def test_dns_resolution():
    print("🔍 DNS域名解析测试...")
    print("=" * 40)
    
    test_domains = ['localhost', 'myblog.local', 'github.com', 'chat.deepseek.com']
    
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain:15} -> {ip}")
        except Exception as e:
            print(f"❌ {domain:15} -> 解析失败: {e}")
def explain_dns():
    print(f"\n📚 DNS解析过程:")
    print("  1. 浏览器输入域名")
    print("  2. 查询本地hosts文件")
    print("  3. 查询本地DNS缓存") 
    print("  4. 查询ISP DNS服务器")
    print("  5. 递归查询根域名服务器")
    print("  6. 返回IP地址")
    print("  7. 建立TCP连接")

if __name__ == '__main__':
    test_dns_resolution()
    explain_dns()
