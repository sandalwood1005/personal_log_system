#!/usr/bin/env python3
"""
兼容Python 3.6的性能基准测试
"""

import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceBenchmark:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {}
    
    def calculate_percentile(self, data, percentile):
        """手动计算百分位数（兼容Python 3.6）"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * percentile / 100
        lower_index = int(index)
        upper_index = lower_index + 1
        
        if upper_index >= len(sorted_data):
            return sorted_data[lower_index]
        
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def test_single_request(self, endpoint="/"):
        """测试单个请求性能"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000  # 转毫秒
            return {
                "status": "success",
                "status_code": response.status_code,
                "response_time": response_time,
                "content_length": len(response.content)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": (time.time() - start_time) * 1000
            }
    
    def test_concurrent_requests(self, endpoint="/", num_requests=20, concurrency=5):
        """测试并发性能"""
        print(f"🚀 测试并发性能: {num_requests}请求, {concurrency}并发")
        
        times = []
        successes = 0
        errors = 0
        
        def worker():
            result = self.test_single_request(endpoint)
            return result
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                times.append(result["response_time"])
                
                if result["status"] == "success":
                    successes += 1
                else:
                    errors += 1
                    print(f"   请求失败: {result['error']}")
        
        total_time = time.time() - start_time
        
        # 计算统计信息（兼容Python 3.6）
        if times:
            min_time = min(times)
            max_time = max(times)
            avg_time = statistics.mean(times)
            p95_time = self.calculate_percentile(times, 95)
        else:
            min_time = max_time = avg_time = p95_time = 0
        
        stats = {
            "total_requests": num_requests,
            "concurrency": concurrency,
            "successes": successes,
            "errors": errors,
            "success_rate": (successes / num_requests) * 100 if num_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min_time,
                "max": max_time,
                "avg": avg_time,
                "p95": p95_time
            }
        }
        
        return stats
    
    def test_different_endpoints(self):
        """测试不同端点的性能"""
        endpoints = [
            ("首页", "/"),
            ("文章页", "/post/1"),  # 假设有ID为1的文章
            ("用户注册页", "/register"),
            ("登录页", "/login"),
        ]
        
        print("📊 测试不同端点性能...")
        print("=" * 60)
        
        for name, endpoint in endpoints:
            print(f"\n测试: {name} ({endpoint})")
            stats = self.test_concurrent_requests(endpoint, num_requests=10, concurrency=3)
            
            print(f"  成功率: {stats['success_rate']:.1f}%")
            print(f"  QPS: {stats['requests_per_second']:.1f} 请求/秒")
            print(f"  平均响应: {stats['response_times']['avg']:.1f}ms")
            print(f"  P95响应: {stats['response_times']['p95']:.1f}ms")
            
            self.results[name] = stats
        
        return self.results
    
    def test_load_capacity(self):
        """测试负载能力"""
        print("\n🔬 测试负载能力...")
        print("=" * 40)
        
        load_tests = [
            ("低负载", 10, 2),
            ("中负载", 30, 5), 
            ("高负载", 50, 10)
        ]
        
        for name, requests, concurrency in load_tests:
            print(f"\n{name}: {requests}请求, {concurrency}并发")
            stats = self.test_concurrent_requests("/", requests, concurrency)
            
            print(f"  QPS: {stats['requests_per_second']:.1f}")
            print(f"  平均响应: {stats['response_times']['avg']:.1f}ms")
            print(f"  成功率: {stats['success_rate']:.1f}%")
            
            self.results[f"负载测试_{name}"] = stats
        
        return self.results
    
    def generate_report(self):
        """生成性能报告"""
        print("\n" + "=" * 60)
        print("🎯 性能基准测试报告")
        print("=" * 60)
        
        if not self.results:
            print("没有测试数据")
            return
        
        # 计算首页性能作为基准
        homepage_stats = self.results.get("首页")
        if homepage_stats:
            avg_response = homepage_stats["response_times"]["avg"]
            qps = homepage_stats["requests_per_second"]
            success_rate = homepage_stats["success_rate"]
            
            print(f"首页性能基准:")
            print(f"  - 平均响应时间: {avg_response:.1f}ms")
            print(f"  - 吞吐量: {qps:.1f} 请求/秒") 
            print(f"  - 成功率: {success_rate:.1f}%")
            
            # 性能评级
            if avg_response < 50:
                rating = "🎉 优秀"
            elif avg_response < 100:
                rating = "✅ 良好" 
            elif avg_response < 200:
                rating = "⚠️  一般"
            else:
                rating = "❌ 需要优化"
            
            print(f"性能评级: {rating}")
        
        # 显示所有端点性能
        print(f"\n各端点性能:")
        for name, stats in self.results.items():
            if not name.startswith("负载测试"):
                print(f"  {name:12} - {stats['response_times']['avg']:6.1f}ms | {stats['success_rate']:5.1f}%")
        
        # 负载测试结果
        print(f"\n负载测试结果:")
        for name, stats in self.results.items():
            if name.startswith("负载测试"):
                print(f"  {name:12} - QPS: {stats['requests_per_second']:5.1f} | 响应: {stats['response_times']['avg']:5.1f}ms")
        
        return self.results

if __name__ == '__main__':
    # 检查服务是否可用
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ 服务可用，开始性能测试...")
    except Exception as e:
        print(f"❌ 服务不可用: {e}")
        print("请先启动服务: systemctl start myblog")
        exit(1)
    
    benchmark = PerformanceBenchmark()
    
    # 测试不同端点
    print("开始端点性能测试...")
    benchmark.test_different_endpoints()
    
    # 测试负载能力
    print("开始负载能力测试...")
    benchmark.test_load_capacity()
    
    # 生成报告
    results = benchmark.generate_report()
    
    # 保存结果
    try:
        with open("performance_results.json", "w") as f:
            import json
            json.dump(results, f, indent=2, default=str)
        print("\n💾 结果已保存到 performance_results.json")
    except Exception as e:
        print(f"保存结果失败: {e}")
