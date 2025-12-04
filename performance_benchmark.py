#!/usr/bin/env python3
"""
综合性能基准测试 - 学习：性能监控、瓶颈分析
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
    
    def test_concurrent_requests(self, endpoint="/", num_requests=50, concurrency=10):
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
        
        total_time = time.time() - start_time
        
        stats = {
            "total_requests": num_requests,
            "concurrency": concurrency,
            "successes": successes,
            "errors": errors,
            "success_rate": (successes / num_requests) * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "response_times": {
                "min": min(times) if times else 0,
                "max": max(times) if times else 0,
                "avg": statistics.mean(times) if times else 0,
                "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else 0
            }
        }
        
        return stats
    
    def test_different_endpoints(self):
        """测试不同端点的性能"""
        endpoints = [
            ("首页", "/"),
            ("文章页", "/post/1"),
            ("分类管理", "/categories"),
            ("用户注册", "/register"),
        ]
        
        print("📊 测试不同端点性能...")
        print("=" * 60)
        
        for name, endpoint in endpoints:
            print(f"\n测试: {name} ({endpoint})")
            stats = self.test_concurrent_requests(endpoint, num_requests=20, concurrency=5)
            
            print(f"  成功率: {stats['success_rate']:.1f}%")
            print(f"  QPS: {stats['requests_per_second']:.1f} 请求/秒")
            print(f"  平均响应: {stats['response_times']['avg']:.1f}ms")
            print(f"  P95响应: {stats['response_times']['p95']:.1f}ms")
            
            self.results[name] = stats
        
        return self.results
    
    def generate_report(self):
        """生成性能报告"""
        print("\n" + "=" * 60)
        print("🎯 性能基准测试报告")
        print("=" * 60)
        
        if not self.results:
            print("没有测试数据")
            return
        
        # 总体统计
        total_requests = sum(stats["total_requests"] for stats in self.results.values())
        total_successes = sum(stats["successes"] for stats in self.results.values())
        avg_qps = statistics.mean(stats["requests_per_second"] for stats in self.results.values())
        avg_response = statistics.mean(stats["response_times"]["avg"] for stats in self.results.values())
        
        print(f"总请求数: {total_requests}")
        print(f"总成功率: {(total_successes/total_requests)*100:.1f}%")
        print(f"平均QPS: {avg_qps:.1f}")
        print(f"平均响应: {avg_response:.1f}ms")
        
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
        
        return self.results

if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    
    # 测试不同端点
    benchmark.test_different_endpoints()
    
    # 生成报告
    results = benchmark.generate_report()
    
    # 保存结果（用于后续对比）
    with open("performance_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2)
    
    print("\n💡 结果已保存到 performance_results.json")
