#!/usr/bin/env python3
"""
兼容Python 3.6的系统资源监控
"""

import psutil
import time
import json
from datetime import datetime

class SystemMonitor:
    def __init__(self, duration=20, interval=2):
        self.duration = duration
        self.interval = interval
        self.metrics = []
    
    def collect_metrics(self):
        """收集系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                },
                "memory": {
                    "total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                    "available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                    "percent": memory.percent,
                    "used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                    "percent": disk.percent,
                },
                "network": {
                    "mb_sent": round(network.bytes_sent / 1024 / 1024, 2),
                    "mb_recv": round(network.bytes_recv / 1024 / 1024, 2),
                }
            }
            return metrics
        except Exception as e:
            print(f"收集指标失败: {e}")
            return None
    
    def monitor_gunicorn(self):
        """监控Gunicorn进程"""
        gunicorn_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                proc_name = proc.info['name'] or ''
                if 'gunicorn' in proc_name.lower():
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                    gunicorn_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc_name,
                        "memory_mb": round(memory_mb, 1),
                        "cpu_percent": round(proc.info['cpu_percent'] or 0, 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return gunicorn_processes
    
    def run_monitoring(self):
        """运行监控"""
        print("🔍 开始系统资源监控...")
        print(f"监控时长: {self.duration}秒, 间隔: {self.interval}秒")
        print("=" * 50)
        
        start_time = time.time()
        sample_count = 0
        
        try:
            while time.time() - start_time < self.duration:
                # 收集系统指标
                system_metrics = self.collect_metrics()
                
                if system_metrics is None:
                    continue
                
                # 收集Gunicorn进程指标
                gunicorn_metrics = self.monitor_gunicorn()
                
                sample = {
                    "system": system_metrics,
                    "gunicorn": gunicorn_metrics
                }
                
                self.metrics.append(sample)
                sample_count += 1
                
                # 打印当前状态
                cpu = system_metrics["cpu"]["percent"]
                memory = system_metrics["memory"]["percent"]
                gunicorn_count = len(gunicorn_metrics)
                
                print(f"样本 {sample_count:2d}: CPU {cpu:5.1f}% | 内存 {memory:5.1f}% | Gunicorn进程: {gunicorn_count}")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n监控被用户中断")
        
        return self.metrics
    
    def generate_report(self):
        """生成监控报告"""
        if not self.metrics:
            print("没有监控数据")
            return
        
        print("\n" + "=" * 50)
        print("📈 系统资源监控报告")
        print("=" * 50)
        
        # 计算统计信息
        cpu_values = [m["system"]["cpu"]["percent"] for m in self.metrics if m["system"]]
        memory_values = [m["system"]["memory"]["percent"] for m in self.metrics if m["system"]]
        
        if not cpu_values:
            print("没有有效的监控数据")
            return
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        max_cpu = max(cpu_values)
        max_memory = max(memory_values)
        
        print(f"CPU使用率:  平均 {avg_cpu:.1f}%, 峰值 {max_cpu:.1f}%")
        print(f"内存使用率: 平均 {avg_memory:.1f}%, 峰值 {max_memory:.1f}%")
        
        # Gunicorn进程统计
        all_gunicorn = []
        for metric in self.metrics:
            all_gunicorn.extend(metric["gunicorn"])
        
        if all_gunicorn:
            unique_pids = set(p["pid"] for p in all_gunicorn)
            memory_values = [p["memory_mb"] for p in all_gunicorn if p["memory_mb"] > 0]
            avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
            
            print(f"Gunicorn进程数: {len(unique_pids)}")
            print(f"进程内存范围: {min(memory_values):.1f}MB - {max(memory_values):.1f}MB")
            print(f"平均内存/进程: {avg_memory:.1f}MB")
        
        # 性能建议
        print("\n💡 性能建议:")
        if max_cpu > 80:
            print("  - CPU使用率较高，考虑优化代码或增加Worker")
        elif max_cpu < 30:
            print("  - CPU资源充足，可以增加并发数")
        else:
            print("  - CPU使用率正常")
            
        if max_memory > 80:
            print("  - 内存使用率较高，检查内存泄漏")
        elif max_memory < 50:
            print("  - 内存资源充足")
        else:
            print("  - 内存使用率正常")
        
        return self.metrics

if __name__ == '__main__':
    # 检查psutil是否安装
    try:
        import psutil
    except ImportError:
        print("安装psutil库...")
        import subprocess
        subprocess.check_call(["pip", "install", "psutil"])
        import psutil
    
    # 运行监控
    monitor = SystemMonitor(duration=20, interval=2)
    print("开始监控系统资源...")
    metrics = monitor.run_monitoring()
    
    # 生成报告
    monitor.generate_report()
    
    # 保存数据
    try:
        with open("system_metrics.json", "w") as f:
            # 使用default参数处理无法序列化的对象
            json.dump(metrics, f, indent=2, default=str)
        print("\n💾 监控数据已保存到 system_metrics.json")
    except Exception as e:
        print(f"保存数据失败: {e}")
