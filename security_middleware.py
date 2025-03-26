from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable, List, Dict, Any
import ipaddress
import re

from app.config import settings
from app.security import ip_blacklist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("security_middleware.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("security_middleware")

# 请求限流中间件
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: FastAPI, 
        rate_limit_per_minute: int = 60,
        burst_limit: int = 100
    ):
        super().__init__(app)
        self.rate_limit_per_minute = rate_limit_per_minute
        self.burst_limit = burst_limit
        self.requests = {}  # IP -> [(timestamp, count), ...]
        self.cleanup_interval = 60  # 清理间隔（秒）
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 定期清理过期的请求记录
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(current_time)
            self.last_cleanup = current_time
        
        # 检查请求限制
        if not self._check_rate_limit(client_ip, current_time):
            # 记录可疑活动
            ip_blacklist.record_suspicious_activity(client_ip)
            
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"}
            )
        
        # 处理请求
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, ip: str, current_time: float) -> bool:
        """检查IP是否超过速率限制"""
        # 初始化IP的请求记录
        if ip not in self.requests:
            self.requests[ip] = [(current_time, 1)]
            return True
        
        # 获取最近一分钟的请求
        minute_ago = current_time - 60
        recent_requests = [(ts, count) for ts, count in self.requests[ip] if ts > minute_ago]
        
        # 计算最近一分钟的请求总数
        total_requests = sum(count for _, count in recent_requests)
        
        # 检查是否超过突发限制
        if len(recent_requests) > 0:
            latest_ts, latest_count = recent_requests[-1]
            if latest_count > self.burst_limit:
                return False
        
        # 检查是否超过每分钟限制
        if total_requests >= self.rate_limit_per_minute:
            return False
        
        # 更新请求记录
        if len(recent_requests) > 0 and recent_requests[-1][0] == current_time:
            # 更新最后一条记录
            recent_requests[-1] = (current_time, recent_requests[-1][1] + 1)
        else:
            # 添加新记录
            recent_requests.append((current_time, 1))
        
        self.requests[ip] = recent_requests
        return True
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """清理过期的请求记录"""
        minute_ago = current_time - 60
        for ip in list(self.requests.keys()):
            self.requests[ip] = [(ts, count) for ts, count in self.requests[ip] if ts > minute_ago]
            if not self.requests[ip]:
                del self.requests[ip]

# SQL注入防护中间件
class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        # SQL注入模式
        self.sql_patterns = [
            r"(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE)(\s|$)",
            r"(\s|^)(UNION|JOIN|OR|AND)(\s|$)",
            r"--",
            r";",
            r"'",
            r"\/\*.*\*\/",
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # 获取请求参数
        query_params = dict(request.query_params)
        
        # 检查查询参数
        for param, value in query_params.items():
            if self._check_sql_injection(value):
                client_ip = request.client.host if request.client else "unknown"
                logger.warning(f"Possible SQL injection attempt from {client_ip}: {param}={value}")
                
                # 记录可疑活动
                ip_blacklist.record_suspicious_activity(client_ip)
                
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request"}
                )
        
        # 处理请求
        response = await call_next(request)
        return response
    
    def _check_sql_injection(self, value: str) -> bool:
        """检查字符串是否包含SQL注入模式"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        
        return False

# XSS防护中间件
class XSSProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        # XSS模式
        self.xss_patterns = [
            r"<script.*?>.*?<\/script>",
            r"javascript:",
            r"onerror=",
            r"onload=",
            r"eval\(",
            r"document\.cookie",
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # 获取请求参数
        query_params = dict(request.query_params)
        
        # 检查查询参数
        for param, value in query_params.items():
            if self._check_xss(value):
                client_ip = request.client.host if request.client else "unknown"
                logger.warning(f"Possible XSS attempt from {client_ip}: {param}={value}")
                
                # 记录可疑活动
                ip_blacklist.record_suspicious_activity(client_ip)
                
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request"}
                )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _check_xss(self, value: str) -> bool:
        """检查字符串是否包含XSS模式"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        
        return False

# 异常流量检测中间件
class AnomalousTrafficDetectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.ip_requests = {}  # IP -> [(timestamp, path), ...]
        self.path_counts = {}  # IP -> {path -> count}
        self.cleanup_interval = 300  # 清理间隔（秒）
        self.last_cleanup = time.time()
        self.detection_window = 60  # 检测窗口（秒）
        self.path_threshold = 10  # 同一路径请求阈值
        self.unique_paths_threshold = 20  # 不同路径请求阈值
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # 获取客户端IP和请求路径
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # 定期清理过期的请求记录
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(current_time)
            self.last_cleanup = current_time
        
        # 记录请求
        self._record_request(client_ip, path, current_time)
        
        # 检查异常流量
        if self._check_anomalous_traffic(client_ip, current_time):
            logger.warning(f"Anomalous traffic detected from IP: {client_ip}")
            
            # 记录可疑活动
            ip_blacklist.record_suspicious_activity(client_ip)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Anomalous traffic detected"}
            )
        
        # 处理请求
        response = await call_next(request)
        return response
    
    def _record_request(self, ip: str, path: str, timestamp: float) -> None:
        """记录请求"""
        # 记录请求时间和路径
        if ip not in self.ip_requests:
            self.ip_requests[ip] = []
        self.ip_requests[ip].append((timestamp, path))
        
        # 记录路径计数
        if ip not in self.path_counts:
            self.path_counts[ip] = {}
        if path not in self.path_counts[ip]:
            self.path_counts[ip][path] = 0
        self.path_counts[ip][path] += 1
    
    def _check_anomalous_traffic(self, ip: str, current_time: float) -> bool:
        """检查IP是否产生异常流量"""
        if ip not in self.ip_requests:
            return False
        
        # 获取检测窗口内的请求
        window_start = current_time - self.detection_window
        recent_requests = [(ts, path) for ts, path in self.ip_requests[ip] if ts > window_start]
        
        # 检查请求总数
        if len(recent_requests) < self.unique_paths_threshold:
            return False
        
        # 检查同一路径的请求数量
        for path, count in self.path_counts[ip].items():
            if count > self.path_threshold:
                return True
        
        # 检查不同路径的请求数量
        unique_paths = set(path for _, path in recent_requests)
        if len(unique_paths) > self.unique_paths_threshold:
            return True
        
        return False
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """清理过期的请求记录"""
        window_start = current_time - self.detection_window
        
        for ip in list(self.ip_requests.keys()):
            # 清理请求记录
            recent_requests = [(ts, path) for ts, path in self.ip_requests[ip] if ts > window_start]
            self.ip_requests[ip] = recent_requests
            
            # 重新计算路径计数
            self.path_counts[ip] = {}
            for _, path in recent_requests:
                if path not in self.path_counts[ip]:
                    self.path_counts[ip][path] = 0
                self.path_counts[ip][path] += 1
            
            # 如果没有请求，删除IP记录
            if not recent_requests:
                del self.ip_requests[ip]
                del self.path_counts[ip]

# 配置安全中间件
def configure_security_middleware(app: FastAPI) -> None:
    """配置所有安全中间件"""
    # 添加IP黑名单中间件
    app.middleware("http")(check_ip_blacklist)
    
    # 添加请求限流中间件
    app.add_middleware(RateLimitMiddleware, rate_limit_per_minute=120, burst_limit=30)
    
    # 添加SQL注入防护中间件
    app.add_middleware(SQLInjectionProtectionMiddleware)
    
    # 添加XSS防护中间件
    app.add_middleware(XSSProtectionMiddleware)
    
    # 添加异常流量检测中间件
    app.add_middleware(AnomalousTrafficDetectionMiddleware)
    
    logger.info("All security middleware configured successfully")
