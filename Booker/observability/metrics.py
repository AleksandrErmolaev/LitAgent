from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Метрики
book_requests_total = Counter(
    'booker_requests_total', 
    'Total book requests', 
    ['source', 'status']
)

book_latency = Histogram(
    'booker_latency_seconds', 
    'Book fetch latency', 
    ['source'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

cache_hits_total = Counter('booker_cache_hits_total', 'Cache hits')
cache_misses_total = Counter('booker_cache_misses_total', 'Cache misses')

book_size_words = Gauge('booker_book_size_words', 'Book size in words', ['title'])


def track_latency(source: str):
    """Декоратор для замера латенси"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                book_latency.labels(source=source).observe(time.time() - start)
                return result
            except Exception as e:
                book_latency.labels(source=source).observe(time.time() - start)
                raise
        return wrapper
    return decorator


def get_metrics():
    """Возвращает метрики в формате Prometheus"""
    return generate_latest()