#!/usr/bin/env python3
"""
Claude 服务并发测试脚本
功能：并发测试 Claude API，统计成功率、错误率和错误类型
"""

import asyncio
import aiohttp
import argparse
import time
import json
import random
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple


class ClaudeLoadTester:
    # 测试消息池 - 包含不同复杂度的测试样本（高Token版本）
    TEST_MESSAGES = [
        # 大型代码审查任务 1
        """Please review the following e-commerce order processing system implementation and provide detailed feedback on architecture, security, performance, and best practices:

```python
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAYMENT_CONFIRMED = "payment_confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class Product:
    id: str
    name: str
    price: float
    stock: int
    category: str

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: float

class OrderProcessor:
    def __init__(self, db_connection, payment_gateway, inventory_service, notification_service):
        self.db = db_connection
        self.payment = payment_gateway
        self.inventory = inventory_service
        self.notifications = notification_service
        self.logger = logging.getLogger(__name__)

    async def create_order(self, user_id: str, items: List[OrderItem], shipping_address: Dict) -> str:
        # Validate inventory
        for item in items:
            stock = await self.inventory.get_stock(item.product_id)
            if stock < item.quantity:
                raise ValueError(f"Insufficient stock for product {item.product_id}")

        # Calculate total
        total = sum(item.price * item.quantity for item in items)

        # Create order in database
        order_id = await self.db.insert_order({
            'user_id': user_id,
            'items': items,
            'total': total,
            'status': OrderStatus.PENDING.value,
            'shipping_address': shipping_address,
            'created_at': datetime.now()
        })

        # Reserve inventory
        for item in items:
            await self.inventory.reserve_stock(item.product_id, item.quantity)

        return order_id

    async def process_payment(self, order_id: str, payment_details: Dict) -> bool:
        order = await self.db.get_order(order_id)

        try:
            payment_result = await self.payment.charge(
                amount=order['total'],
                currency='USD',
                payment_method=payment_details
            )

            if payment_result['status'] == 'success':
                await self.db.update_order_status(order_id, OrderStatus.PAYMENT_CONFIRMED)
                await self.notifications.send_email(
                    order['user_id'],
                    'Payment Confirmed',
                    f'Your payment for order {order_id} has been confirmed'
                )
                return True
            else:
                await self.handle_payment_failure(order_id)
                return False

        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            await self.handle_payment_failure(order_id)
            return False

    async def handle_payment_failure(self, order_id: str):
        order = await self.db.get_order(order_id)

        # Release reserved inventory
        for item in order['items']:
            await self.inventory.release_stock(item['product_id'], item['quantity'])

        await self.db.update_order_status(order_id, OrderStatus.CANCELLED)
        await self.notifications.send_email(
            order['user_id'],
            'Order Cancelled',
            f'Order {order_id} has been cancelled due to payment failure'
        )

    async def ship_order(self, order_id: str, tracking_number: str):
        await self.db.update_order(order_id, {
            'status': OrderStatus.SHIPPED.value,
            'tracking_number': tracking_number,
            'shipped_at': datetime.now()
        })

        order = await self.db.get_order(order_id)
        await self.notifications.send_email(
            order['user_id'],
            'Order Shipped',
            f'Your order {order_id} has been shipped. Tracking: {tracking_number}'
        )
```

Please analyze:
1. Potential race conditions and concurrency issues
2. Error handling and transaction management
3. Security vulnerabilities (e.g., SQL injection, price manipulation)
4. Performance bottlenecks
5. Missing validations or edge cases
6. Suggested improvements and refactoring opportunities
""",

        # 大型系统设计问题
        """Design a distributed rate limiting system for a high-traffic API gateway that serves millions of requests per second.

Requirements:
1. Support different rate limiting strategies (token bucket, leaky bucket, fixed window, sliding window)
2. Per-user, per-IP, and per-API-key rate limiting
3. Distributed across multiple data centers globally
4. Low latency (<10ms overhead)
5. High accuracy (>99% correct limiting decisions)
6. Support for burst traffic
7. Graceful degradation when backend systems fail
8. Real-time monitoring and alerting
9. Dynamic rate limit updates without service restart
10. Cost-effective for billions of requests per day

Please provide:
- High-level architecture diagram explanation
- Technology stack recommendations (databases, caching, message queues)
- Data structures and algorithms for each rate limiting strategy
- Handling of edge cases (clock skew, network partitions, cache inconsistency)
- Scalability considerations
- Monitoring and observability approach
- Example implementation pseudocode for sliding window rate limiter
- Trade-offs between different approaches
""",

        # 复杂数据处理任务
        """Given the following complex nested JSON data representing a company's organizational structure and employee data, write a comprehensive Python solution to:

```json
{
  "company": "TechCorp",
  "departments": [
    {
      "id": "dept-001",
      "name": "Engineering",
      "budget": 5000000,
      "manager": "emp-123",
      "teams": [
        {
          "id": "team-001",
          "name": "Backend",
          "lead": "emp-456",
          "members": [
            {
              "employee_id": "emp-456",
              "name": "Alice Johnson",
              "role": "Senior Backend Engineer",
              "salary": 150000,
              "skills": ["Python", "Go", "PostgreSQL", "Kubernetes"],
              "projects": [
                {"id": "proj-001", "name": "API Gateway", "hours": 120, "status": "active"},
                {"id": "proj-002", "name": "Database Migration", "hours": 80, "status": "completed"}
              ],
              "performance_reviews": [
                {"date": "2024-01-15", "rating": 4.5, "reviewer": "emp-123"},
                {"date": "2024-07-15", "rating": 4.8, "reviewer": "emp-123"}
              ]
            },
            {
              "employee_id": "emp-789",
              "name": "Bob Smith",
              "role": "Backend Engineer",
              "salary": 120000,
              "skills": ["Java", "Spring Boot", "MySQL", "Redis"],
              "projects": [
                {"id": "proj-001", "name": "API Gateway", "hours": 160, "status": "active"}
              ],
              "performance_reviews": [
                {"date": "2024-02-20", "rating": 4.2, "reviewer": "emp-456"}
              ]
            }
          ]
        },
        {
          "id": "team-002",
          "name": "Frontend",
          "lead": "emp-321",
          "members": [
            {
              "employee_id": "emp-321",
              "name": "Carol White",
              "role": "Senior Frontend Engineer",
              "salary": 145000,
              "skills": ["React", "TypeScript", "GraphQL", "CSS"],
              "projects": [
                {"id": "proj-003", "name": "Dashboard Redesign", "hours": 200, "status": "active"}
              ],
              "performance_reviews": [
                {"date": "2024-03-10", "rating": 4.6, "reviewer": "emp-123"}
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "dept-002",
      "name": "Product",
      "budget": 3000000,
      "manager": "emp-111",
      "teams": [
        {
          "id": "team-003",
          "name": "Product Management",
          "lead": "emp-111",
          "members": [
            {
              "employee_id": "emp-111",
              "name": "David Brown",
              "role": "VP of Product",
              "salary": 200000,
              "skills": ["Product Strategy", "User Research", "Roadmapping"],
              "projects": [
                {"id": "proj-004", "name": "Q4 Product Roadmap", "hours": 100, "status": "active"}
              ],
              "performance_reviews": [
                {"date": "2024-01-05", "rating": 4.9, "reviewer": "CEO"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Tasks:
1. Calculate total salary expenditure per department and team
2. Find top 5 employees by average performance rating
3. List all employees working on active projects with their total hours
4. Generate a skills matrix showing which skills are most common
5. Calculate the average salary by role
6. Find employees who are overallocated (>160 hours across all active projects)
7. Generate a report of all projects with their team members and total hours
8. Find the department with the best average performance ratings
9. List employees due for performance review (last review >6 months ago)
10. Calculate budget utilization percentage per department

Provide efficient, clean, well-documented Python code with proper error handling.
""",

        # 算法优化问题
        """I have a performance-critical system that processes millions of log entries per second. Each log entry contains:
- timestamp (Unix timestamp in milliseconds)
- user_id (string, 32 characters)
- event_type (enum: LOGIN, LOGOUT, PAGE_VIEW, API_CALL, ERROR)
- metadata (JSON object, variable size up to 1KB)

Current implementation:
```python
class LogProcessor:
    def __init__(self):
        self.logs = []
        self.user_sessions = {}
        self.event_counts = {}

    def process_log(self, log_entry):
        # Add to memory
        self.logs.append(log_entry)

        # Update user session
        user_id = log_entry['user_id']
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(log_entry)

        # Update event counts
        event_type = log_entry['event_type']
        if event_type not in self.event_counts:
            self.event_counts[event_type] = 0
        self.event_counts[event_type] += 1

    def get_user_events(self, user_id, start_time, end_time):
        if user_id not in self.user_sessions:
            return []
        return [
            log for log in self.user_sessions[user_id]
            if start_time <= log['timestamp'] <= end_time
        ]

    def get_event_count(self, event_type):
        return self.event_counts.get(event_type, 0)

    def get_recent_errors(self, last_n_minutes):
        cutoff = time.time() * 1000 - (last_n_minutes * 60 * 1000)
        return [
            log for log in self.logs
            if log['event_type'] == 'ERROR' and log['timestamp'] >= cutoff
        ]
```

Problems:
1. Memory usage grows unbounded - crashes after a few hours
2. Query performance degrades over time (get_user_events takes >10 seconds after 1M logs)
3. get_recent_errors scans entire log list every time
4. No persistence - data lost on restart
5. Not thread-safe for concurrent processing
6. No cleanup of old data

Please design and implement a better solution that:
- Handles millions of logs per second efficiently
- Keeps memory usage bounded (max 10GB)
- Maintains fast query performance (queries <100ms)
- Persists data to disk reliably
- Supports concurrent processing
- Automatically cleans up old data (>30 days)
- Provides aggregate statistics (events per minute, unique users, error rates)

Include specific data structures, algorithms, and code implementation.
""",

        # 数据库设计问题
        """Design a database schema for a social media platform similar to Twitter/X with the following features:

Core Features:
1. Users can post tweets (max 280 characters) with optional media (images, videos)
2. Users can follow/unfollow other users
3. Users can like, retweet, quote tweets, and reply to tweets
4. Real-time timeline showing tweets from followed users
5. Trending topics and hashtags
6. Direct messaging between users
7. Notifications (likes, retweets, mentions, new followers)
8. User profiles with bio, avatar, banner, location
9. Tweet search with filters (date range, user, hashtags, media type)
10. Analytics (impressions, engagement rate, follower growth)

Scale Requirements:
- 500 million users
- 200 million daily active users
- 500 million tweets per day
- Average user follows 200 people
- Support for 10,000 tweets per second during peak
- Timeline queries must return in <200ms
- Search queries must return in <500ms

Please provide:
1. Complete database schema with all tables and relationships
2. Indexing strategy for optimal query performance
3. Partitioning/sharding strategy for horizontal scaling
4. Caching strategy (what to cache, invalidation approach)
5. How to handle the timeline query efficiently (fan-out on write vs fan-out on read)
6. How to implement trending topics calculation
7. Storage optimization for media files
8. Database technology choices (SQL vs NoSQL, which databases for which use cases)
9. Sample queries for common operations with explain plans
10. Migration strategy for schema changes with zero downtime

Include SQL DDL statements, query examples, and architectural diagrams explanation.
""",

        # 微服务架构设计
        """Design a microservices architecture for an online food delivery platform similar to UberEats/DoorDash.

Business Requirements:
1. Customer app: Browse restaurants, place orders, track delivery, rate restaurants
2. Restaurant app: Receive orders, update menu, manage availability
3. Driver app: Accept deliveries, navigate, update delivery status
4. Admin dashboard: Monitor operations, handle disputes, analytics

Technical Requirements:
1. Handle 100,000 concurrent users
2. Process 10,000 orders per hour during peak
3. Real-time order tracking (location updates every 5 seconds)
4. 99.9% uptime SLA
5. Support multiple payment methods
6. Integration with third-party services (maps, payments, SMS)
7. Multi-region deployment (US, EU, APAC)
8. GDPR and PCI-DSS compliance

Please design:
1. Microservice boundaries (which services, what responsibilities)
2. Communication patterns (sync vs async, REST vs gRPC vs message queues)
3. Data storage strategy (which database for which service)
4. Event-driven architecture for order lifecycle
5. Real-time location tracking implementation
6. Payment processing flow with failure handling
7. API gateway configuration and rate limiting
8. Service discovery and load balancing
9. Circuit breakers and retry policies
10. Monitoring, logging, and distributed tracing setup
11. Deployment strategy (Kubernetes, service mesh)
12. Security implementation (authentication, authorization, encryption)

Include:
- Architecture diagram explanation
- API contracts for key services
- Event schemas for async communication
- Database schemas for each service
- Sequence diagrams for critical flows (order placement, delivery tracking)
- Failure scenarios and mitigation strategies
- Performance optimization techniques
""",

        # 安全审计问题
        """Perform a comprehensive security audit of the following authentication and authorization system:

```python
from flask import Flask, request, jsonify, session
import hashlib
import sqlite3
import jwt
import datetime

app = Flask(__name__)
app.secret_key = "my-secret-key-12345"

def get_db():
    conn = sqlite3.connect('users.db')
    return conn

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data.get('email', '')

    # Hash password
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # Insert into database
    db = get_db()
    cursor = db.cursor()
    query = f"INSERT INTO users (username, password, email, role) VALUES ('{username}', '{password_hash}', '{email}', 'user')"
    cursor.execute(query)
    db.commit()
    db.close()

    return jsonify({"message": "User registered successfully"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    password_hash = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'"
    cursor.execute(query)
    user = cursor.fetchone()
    db.close()

    if user:
        # Create JWT token
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'role': user[4],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, 'jwt-secret-key', algorithm='HS256')

        session['user_id'] = user[0]

        return jsonify({"token": token, "message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "No token provided"}), 403

    try:
        decoded = jwt.decode(token.replace('Bearer ', ''), 'jwt-secret-key', algorithms=['HS256'])
    except:
        return jsonify({"message": "Invalid token"}), 403

    db = get_db()
    cursor = db.cursor()
    query = f"SELECT username, email, role FROM users WHERE id={user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            "username": user[0],
            "email": user[1],
            "role": user[2]
        })
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/api/users/<user_id>/update', methods=['POST'])
def update_user(user_id):
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "No token provided"}), 403

    decoded = jwt.decode(token.replace('Bearer ', ''), 'jwt-secret-key', algorithms=['HS256'])

    data = request.get_json()

    db = get_db()
    cursor = db.cursor()

    # Update user fields
    if 'email' in data:
        query = f"UPDATE users SET email='{data['email']}' WHERE id={user_id}"
        cursor.execute(query)

    if 'role' in data:
        query = f"UPDATE users SET role='{data['role']}' WHERE id={user_id}"
        cursor.execute(query)

    db.commit()
    db.close()

    return jsonify({"message": "User updated successfully"})

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    token = request.headers.get('Authorization')
    decoded = jwt.decode(token.replace('Bearer ', ''), 'jwt-secret-key', algorithms=['HS256'])

    if decoded['role'] != 'admin':
        return jsonify({"message": "Unauthorized"}), 403

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    db.close()

    return jsonify({"users": users})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

Please identify and explain:
1. All security vulnerabilities (SQL injection, XSS, CSRF, etc.)
2. Authentication and authorization weaknesses
3. Cryptographic issues
4. Session management problems
5. Input validation gaps
6. Information disclosure risks
7. Missing security headers
8. Logging and monitoring gaps
9. Rate limiting and DoS vulnerabilities
10. Compliance issues (GDPR, OWASP Top 10)

For each vulnerability, provide:
- Severity rating (Critical, High, Medium, Low)
- Exploitation scenario
- Impact assessment
- Detailed fix with secure code example
- Additional security best practices recommendations
""",

        # 性能优化问题
        """Optimize the following slow-performing web application backend:

Current System:
- Flask web server with 10 workers
- PostgreSQL database (single instance, 16GB RAM, 8 cores)
- Redis cache (2GB)
- Average response time: 3-5 seconds
- Peak load: 1000 requests per second
- Database has 50 million records in main table

Problem Code:
```python
@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    per_page = 50

    # Database query
    sql = '''
        SELECT p.*, c.name as category_name, u.username as seller_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.seller_id = u.id
        WHERE p.title LIKE %s OR p.description LIKE %s
    '''

    params = [f'%{query}%', f'%{query}%']

    if category:
        sql += ' AND c.name = %s'
        params.append(category)

    sql += ' ORDER BY p.created_at DESC LIMIT %s OFFSET %s'
    params.extend([per_page, (page - 1) * per_page])

    cursor = db.execute(sql, params)
    products = cursor.fetchall()

    # Get review counts and ratings for each product
    for product in products:
        reviews_sql = 'SELECT COUNT(*), AVG(rating) FROM reviews WHERE product_id = %s'
        review_data = db.execute(reviews_sql, [product['id']]).fetchone()
        product['review_count'] = review_data[0]
        product['avg_rating'] = review_data[1]

        # Get seller info
        seller_sql = 'SELECT username, avatar_url, rating FROM users WHERE id = %s'
        seller = db.execute(seller_sql, [product['seller_id']]).fetchone()
        product['seller'] = seller

        # Check if in user's wishlist
        if current_user:
            wishlist_sql = 'SELECT 1 FROM wishlists WHERE user_id = %s AND product_id = %s'
            in_wishlist = db.execute(wishlist_sql, [current_user.id, product['id']]).fetchone()
            product['in_wishlist'] = bool(in_wishlist)

    # Get total count for pagination
    count_sql = 'SELECT COUNT(*) FROM products p JOIN categories c ON p.category_id = c.id WHERE p.title LIKE %s OR p.description LIKE %s'
    count_params = [f'%{query}%', f'%{query}%']
    if category:
        count_sql += ' AND c.name = %s'
        count_params.append(category)

    total = db.execute(count_sql, count_params).fetchone()[0]

    return jsonify({
        'products': products,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    })
```

Issues:
1. N+1 query problem (database calls in loop)
2. No proper indexing
3. LIKE queries are slow on large tables
4. No caching strategy
5. Fetching data not always needed
6. No connection pooling
7. Synchronous I/O blocking
8. No query result pagination optimization

Provide optimized solution with:
1. Rewritten SQL with proper JOINs
2. Index recommendations
3. Caching strategy (what to cache, when to invalidate)
4. Database query optimization techniques
5. Application code improvements
6. Asynchronous processing where applicable
7. Load testing results comparison
8. Monitoring and profiling approach
9. Scalability recommendations
10. Cost-performance trade-offs analysis
"""
    ]

    def __init__(self, endpoint: str, api_key: str, concurrency: int, total_requests: int, model: str = "claude-sonnet-4-5-20250929"):
        self.endpoint = endpoint
        self.api_key = api_key
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.model = model

        # 统计数据
        self.success_count = 0
        self.failure_count = 0
        self.error_types = defaultdict(int)
        self.response_times = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.lock = asyncio.Lock()

    async def send_request(self, session: aiohttp.ClientSession, request_id: int) -> Tuple[bool, float, str]:
        """发送单个请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "claude-cli/1.0",
            "X-App": "cli"
        }

        # 随机选择一个测试消息
        message_content = random.choice(self.TEST_MESSAGES)

        payload = {
            "model": self.model,
            "max_tokens": 2048,  # 增加max_tokens以支持更复杂的回答
            "messages": [
                {"role": "user", "content": message_content}
            ]
        }

        start_time = time.time()
        error_msg = ""

        try:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)  # 增加超时时间以支持复杂任务
            ) as response:
                elapsed = time.time() - start_time

                if response.status == 200:
                    response_data = await response.json()  # 读取完整响应

                    # 统计token使用量
                    if 'usage' in response_data:
                        usage = response_data['usage']
                        input_tokens = usage.get('input_tokens', 0)
                        output_tokens = usage.get('output_tokens', 0)
                        async with self.lock:
                            self.total_input_tokens += input_tokens
                            self.total_output_tokens += output_tokens

                    return True, elapsed, ""
                else:
                    error_text = await response.text()
                    try:
                        error_json = json.loads(error_text)
                        error_msg = f"HTTP {response.status}: {error_json.get('error', {}).get('type', 'unknown')} - {error_json.get('error', {}).get('message', error_text[:100])}"
                    except:
                        error_msg = f"HTTP {response.status}: {error_text[:100]}"
                    return False, elapsed, error_msg

        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            return False, elapsed, "Timeout (>60s)"
        except aiohttp.ClientError as e:
            elapsed = time.time() - start_time
            return False, elapsed, f"ClientError: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, elapsed, f"Exception: {type(e).__name__}: {str(e)}"

    async def worker(self, session: aiohttp.ClientSession, queue: asyncio.Queue, progress_bar: bool = True):
        """工作协程"""
        while True:
            try:
                request_id = await asyncio.wait_for(queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            except:
                break

            if request_id is None:
                queue.task_done()
                break

            success, elapsed, error_msg = await self.send_request(session, request_id)

            async with self.lock:
                self.response_times.append(elapsed)

                if success:
                    self.success_count += 1
                    if progress_bar:
                        print(f"\r进度: {self.success_count + self.failure_count}/{self.total_requests} | 成功: {self.success_count} | 失败: {self.failure_count}", end="", flush=True)
                else:
                    self.failure_count += 1
                    self.error_types[error_msg] += 1
                    if progress_bar:
                        print(f"\r进度: {self.success_count + self.failure_count}/{self.total_requests} | 成功: {self.success_count} | 失败: {self.failure_count}", end="", flush=True)

            queue.task_done()

    async def run_test(self):
        """运行负载测试"""
        print(f"\n{'='*60}")
        print(f"Claude 服务负载测试")
        print(f"{'='*60}")
        print(f"端点: {self.endpoint}")
        print(f"模型: {self.model}")
        print(f"并发数: {self.concurrency}")
        print(f"总请求数: {self.total_requests}")
        print(f"测试样本: {len(self.TEST_MESSAGES)} 种不同复杂度的消息（随机选择）")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # 创建队列
        queue = asyncio.Queue()
        for i in range(self.total_requests):
            await queue.put(i)

        # 添加结束标记
        for _ in range(self.concurrency):
            await queue.put(None)

        # 创建会话和工作协程
        connector = aiohttp.TCPConnector(limit=self.concurrency)
        async with aiohttp.ClientSession(connector=connector) as session:
            start_time = time.time()

            workers = [
                asyncio.create_task(self.worker(session, queue))
                for _ in range(self.concurrency)
            ]

            # 等待所有任务完成
            await queue.join()

            # 取消工作协程
            for w in workers:
                w.cancel()

            total_time = time.time() - start_time

        # 打印统计结果
        self.print_stats(total_time)

    def print_stats(self, total_time: float):
        """打印统计结果"""
        print(f"\n\n{'='*60}")
        print(f"测试结果统计")
        print(f"{'='*60}")

        total = self.success_count + self.failure_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        failure_rate = (self.failure_count / total * 100) if total > 0 else 0

        print(f"\n总体统计:")
        print(f"  总请求数: {total}")
        print(f"  成功数: {self.success_count}")
        print(f"  失败数: {self.failure_count}")
        print(f"  成功率: {success_rate:.2f}%")
        print(f"  失败率: {failure_rate:.2f}%")
        print(f"  总耗时: {total_time:.2f}s")
        print(f"  QPS: {total / total_time:.2f} req/s")

        if self.total_input_tokens > 0 or self.total_output_tokens > 0:
            total_tokens = self.total_input_tokens + self.total_output_tokens
            avg_input = self.total_input_tokens / self.success_count if self.success_count > 0 else 0
            avg_output = self.total_output_tokens / self.success_count if self.success_count > 0 else 0
            print(f"\nToken 使用统计:")
            print(f"  输入 Tokens: {self.total_input_tokens:,} (平均: {avg_input:.0f}/请求)")
            print(f"  输出 Tokens: {self.total_output_tokens:,} (平均: {avg_output:.0f}/请求)")
            print(f"  总计 Tokens: {total_tokens:,}")

        if self.response_times:
            sorted_times = sorted(self.response_times)
            print(f"\n响应时间统计:")
            print(f"  最小值: {min(self.response_times)*1000:.2f}ms")
            print(f"  最大值: {max(self.response_times)*1000:.2f}ms")
            print(f"  平均值: {sum(self.response_times)/len(self.response_times)*1000:.2f}ms")
            print(f"  P50: {sorted_times[len(sorted_times)//2]*1000:.2f}ms")
            print(f"  P90: {sorted_times[int(len(sorted_times)*0.9)]*1000:.2f}ms")
            print(f"  P95: {sorted_times[int(len(sorted_times)*0.95)]*1000:.2f}ms")
            print(f"  P99: {sorted_times[int(len(sorted_times)*0.99)]*1000:.2f}ms")

        if self.error_types:
            print(f"\n错误类型分布:")
            sorted_errors = sorted(self.error_types.items(), key=lambda x: x[1], reverse=True)
            for error_msg, count in sorted_errors:
                percentage = (count / self.failure_count * 100) if self.failure_count > 0 else 0
                print(f"  [{count}次, {percentage:.1f}%] {error_msg}")

        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Claude 服务并发负载测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 10 个并发，发送 100 个请求
  python claude_load_test.py -c 10 -n 100 -e https://api.anthropic.com/v1/messages -k sk-xxx

  # 使用 50 个并发，发送 1000 个请求，指定模型
  python claude_load_test.py -c 50 -n 1000 -e https://your-endpoint.com/v1/messages -k your-api-key -m claude-3-5-sonnet-20241022
        """
    )

    parser.add_argument("-e", "--endpoint", required=True, help="Claude API 端点 URL (例如: https://api.anthropic.com/v1/messages)")
    parser.add_argument("-k", "--api-key", required=True, help="API Key")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="并发数 (默认: 10)")
    parser.add_argument("-n", "--num-requests", type=int, default=100, help="总请求数 (默认: 100)")
    parser.add_argument("-m", "--model", default="claude-sonnet-4-5-20250929", help="模型名称 (默认: claude-sonnet-4-5-20250929)")

    args = parser.parse_args()

    # 创建测试器并运行
    tester = ClaudeLoadTester(
        endpoint=args.endpoint,
        api_key=args.api_key,
        concurrency=args.concurrency,
        total_requests=args.num_requests,
        model=args.model
    )

    asyncio.run(tester.run_test())


if __name__ == "__main__":
    main()
