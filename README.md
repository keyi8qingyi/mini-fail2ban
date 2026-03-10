# Mini Fail2Ban 守护进程版本

支持后台运行、配置文件热加载、systemd 集成的完整版本。

## 🎯 新增功能

- ✅ **后台守护进程** - 作为系统服务运行
- ✅ **配置文件管理** - JSON 格式配置，易于修改
- ✅ **热加载配置** - 无需重启即可应用新配置
- ✅ **systemd 集成** - 完整的服务管理
- ✅ **进程管理** - start/stop/restart/reload/status
- ✅ **日志记录** - 独立的日志文件
- ✅ **白名单支持** - 支持 CIDR 格式
- ✅ **一键安装** - 自动化安装脚本

## 📦 文件说明

```
mini-fail2ban/
├── mini_fail2ban_daemon.py    # 守护进程主程序
├── config.json                 # 配置文件示例
├── mini-fail2ban.service       # systemd 服务文件
├── install.sh                  # 一键安装脚本
└── DAEMON_README.md           # 本文档
```

## 🚀 快速安装

### 方法 1: 一键安装（推荐）

```bash
# 1. 下载所有文件到当前目录
# 2. 运行安装脚本
sudo bash install.sh
```

安装后的目录结构：
```
/opt/mini-fail2ban/              # 程序目录
  └── mini_fail2ban_daemon.py
/etc/mini-fail2ban/              # 配置目录
  └── config.json
/var/log/mini-fail2ban.log       # 日志文件
/var/run/mini-fail2ban.pid       # PID 文件
/usr/local/bin/mini-fail2ban     # 管理命令
```

### 方法 2: 手动安装

```bash
# 1. 创建目录
sudo mkdir -p /opt/mini-fail2ban
sudo mkdir -p /etc/mini-fail2ban

# 2. 复制文件
sudo cp mini_fail2ban_daemon.py /opt/mini-fail2ban/
sudo cp config.json /etc/mini-fail2ban/
sudo cp mini-fail2ban.service /etc/systemd/system/

# 3. 设置权限
sudo chmod +x /opt/mini-fail2ban/mini_fail2ban_daemon.py

# 4. 重载 systemd
sudo systemctl daemon-reload
```

## ⚙️ 配置文件

配置文件位置: `/etc/mini-fail2ban/config.json`

```json
{
  "log_path": "/var/log/auth.log",      // SSH 日志文件路径
  "log_file": "/var/log/mini-fail2ban.log",  // 程序日志文件
  "max_retry": 3,                        // 最大失败次数
  "ban_time": 300,                       // 封禁时长（秒）
  "find_time": 600,                      // 统计时间窗口（秒）
  "whitelist": [                         // IP 白名单
    "127.0.0.1",                         // 单个 IP
    "::1",                               // IPv6
    "192.168.0.0/16",                    // CIDR 格式
    "10.0.0.0/8"
  ],
  "enabled": true                        // 是否启用
}
```

### 配置说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `log_path` | string | `/var/log/auth.log` | SSH 日志文件路径 |
| `log_file` | string | `/var/log/mini-fail2ban.log` | 程序日志文件路径 |
| `max_retry` | int | `3` | 触发封禁的最大失败次数 |
| `ban_time` | int | `300` | 封禁时长（秒） |
| `find_time` | int | `600` | 统计时间窗口（秒） |
| `whitelist` | array | `[]` | IP 白名单列表 |
| `enabled` | bool | `true` | 是否启用防护 |

## 🎮 使用方法

### 使用管理命令（推荐）

安装后会创建 `mini-fail2ban` 命令：

```bash
# 启动服务
mini-fail2ban start

# 停止服务
mini-fail2ban stop

# 重启服务
mini-fail2ban restart

# 重新加载配置（不中断服务）
mini-fail2ban reload

# 查看状态
mini-fail2ban status

# 查看日志
mini-fail2ban logs

# 编辑配置
mini-fail2ban config

# 查看已封禁的 IP
mini-fail2ban banned

# 手动解封 IP
mini-fail2ban unban 192.168.1.100

# 开机自启
mini-fail2ban enable

# 禁用自启
mini-fail2ban disable
```

### 使用 systemd 命令

```bash
# 启动服务
sudo systemctl start mini-fail2ban

# 停止服务
sudo systemctl stop mini-fail2ban

# 重启服务
sudo systemctl restart mini-fail2ban

# 重新加载配置
sudo systemctl reload mini-fail2ban

# 查看状态
sudo systemctl status mini-fail2ban

# 查看日志
sudo journalctl -u mini-fail2ban -f

# 开机自启
sudo systemctl enable mini-fail2ban

# 禁用自启
sudo systemctl disable mini-fail2ban
```

### 使用 Python 脚本

```bash
# 启动
sudo python3 /opt/mini-fail2ban/mini_fail2ban_daemon.py start

# 停止
sudo python3 /opt/mini-fail2ban/mini_fail2ban_daemon.py stop

# 重启
sudo python3 /opt/mini-fail2ban/mini_fail2ban_daemon.py restart

# 重新加载配置
sudo python3 /opt/mini-fail2ban/mini_fail2ban_daemon.py reload

# 查看状态
sudo python3 /opt/mini-fail2ban/mini_fail2ban_daemon.py status
```

## 🔄 配置热加载

修改配置后，有三种方式应用新配置：

### 方法 1: 使用 reload 命令（推荐）

```bash
# 1. 编辑配置
sudo nano /etc/mini-fail2ban/config.json

# 2. 重新加载配置（不中断服务）
mini-fail2ban reload
```

### 方法 2: 发送 SIGHUP 信号

```bash
# 1. 编辑配置
sudo nano /etc/mini-fail2ban/config.json

# 2. 发送信号
sudo kill -HUP $(cat /var/run/mini-fail2ban.pid)
```

### 方法 3: 自动检测（每 5 秒）

程序会自动检测配置文件的修改时间，如果发现变化会自动重新加载。

## 📊 监控和日志

### 查看实时日志

```bash
# 方法 1: 使用管理命令
mini-fail2ban logs

# 方法 2: 使用 tail
sudo tail -f /var/log/mini-fail2ban.log

# 方法 3: 使用 journalctl
sudo journalctl -u mini-fail2ban -f
```

### 日志格式

```
[2024-03-10 15:30:45] [INFO] Mini Fail2Ban 守护进程启动
[2024-03-10 15:30:45] [INFO] 配置文件: /etc/mini-fail2ban/config.json
[2024-03-10 15:30:45] [INFO] 开始监控日志: /var/log/auth.log
[2024-03-10 15:31:20] [INFO] 检测到失败登录: 203.0.113.42 (1/3)
[2024-03-10 15:31:25] [INFO] 检测到失败登录: 203.0.113.42 (2/3)
[2024-03-10 15:31:30] [INFO] 检测到失败登录: 203.0.113.42 (3/3)
[2024-03-10 15:31:30] [WARN] 封禁 IP: 203.0.113.42 (封禁 300 秒，至 15:36:30)
[2024-03-10 15:36:30] [INFO] 解封 IP: 203.0.113.42
```

### 查看封禁状态

```bash
# 查看所有封禁的 IP
mini-fail2ban banned

# 或使用 iptables
sudo iptables -L INPUT -n -v | grep DROP
```

## 🔧 常见操作

### 临时禁用防护

```bash
# 方法 1: 修改配置文件
sudo nano /etc/mini-fail2ban/config.json
# 将 "enabled": true 改为 "enabled": false

# 方法 2: 停止服务
mini-fail2ban stop
```

### 修改封禁时长

```bash
# 1. 编辑配置
sudo nano /etc/mini-fail2ban/config.json
# 修改 "ban_time": 300 为你想要的秒数

# 2. 重新加载
mini-fail2ban reload
```

### 添加白名单

```bash
# 1. 编辑配置
sudo nano /etc/mini-fail2ban/config.json

# 2. 在 whitelist 中添加 IP
{
  "whitelist": [
    "127.0.0.1",
    "192.168.1.100",      # 添加单个 IP
    "10.0.0.0/8"          # 添加整个网段
  ]
}

# 3. 重新加载
mini-fail2ban reload
```

### 手动解封 IP

```bash
# 方法 1: 使用管理命令
mini-fail2ban unban 203.0.113.42

# 方法 2: 使用 iptables
sudo iptables -D INPUT -s 203.0.113.42 -j DROP
```

### 清空所有封禁

```bash
# 重启服务会自动清空
mini-fail2ban restart
```

## 🧪 测试

### 测试配置文件

```bash
# 1. 创建测试配置
cat > /tmp/test-config.json << EOF
{
  "log_path": "/tmp/test-auth.log",
  "log_file": "/tmp/test-fail2ban.log",
  "max_retry": 2,
  "ban_time": 60,
  "find_time": 300,
  "whitelist": ["127.0.0.1"],
  "enabled": true
}
EOF

# 2. 使用测试配置启动
sudo python3 mini_fail2ban_daemon.py start -c /tmp/test-config.json

# 3. 生成测试日志
echo "$(date '+%b %d %H:%M:%S') testhost sshd[12345]: Failed password for root from 203.0.113.42 port 22 ssh2" >> /tmp/test-auth.log
echo "$(date '+%b %d %H:%M:%S') testhost sshd[12346]: Failed password for root from 203.0.113.42 port 22 ssh2" >> /tmp/test-auth.log

# 4. 查看日志
tail -f /tmp/test-fail2ban.log
```

### 测试热加载

```bash
# 1. 启动服务
mini-fail2ban start

# 2. 修改配置（比如改变 max_retry）
sudo nano /etc/mini-fail2ban/config.json

# 3. 重新加载
mini-fail2ban reload

# 4. 查看日志确认
mini-fail2ban logs
```

## 🔍 故障排查

### 服务无法启动

```bash
# 1. 查看详细状态
sudo systemctl status mini-fail2ban -l

# 2. 查看日志
sudo journalctl -u mini-fail2ban -n 50

# 3. 检查权限
ls -la /opt/mini-fail2ban/
ls -la /etc/mini-fail2ban/

# 4. 检查配置文件
cat /etc/mini-fail2ban/config.json | python3 -m json.tool
```

### 配置不生效

```bash
# 1. 确认配置文件路径
mini-fail2ban status

# 2. 验证 JSON 格式
python3 -m json.tool /etc/mini-fail2ban/config.json

# 3. 重新加载配置
mini-fail2ban reload

# 4. 查看日志
mini-fail2ban logs
```

### IP 没有被封禁

```bash
# 1. 检查日志文件路径是否正确
cat /etc/mini-fail2ban/config.json | grep log_path

# 2. 检查日志文件是否有新内容
sudo tail -f /var/log/auth.log

# 3. 检查 IP 是否在白名单
cat /etc/mini-fail2ban/config.json | grep -A 10 whitelist

# 4. 查看程序日志
mini-fail2ban logs
```

## 📈 性能优化

### 日志轮转

```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/mini-fail2ban
```

```
/var/log/mini-fail2ban.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    postrotate
        systemctl reload mini-fail2ban > /dev/null 2>&1 || true
    endscript
}
```

## 🔐 安全建议

1. **定期检查日志**: 了解攻击情况
2. **合理设置阈值**: 避免误封正常用户
3. **维护白名单**: 添加可信 IP
4. **配合其他措施**: SSH 密钥认证、修改端口等
5. **监控封禁列表**: 定期清理过期规则

## 🆚 对比

| 特性 | 简单版 | 守护进程版 |
|------|--------|-----------|
| 后台运行 | ❌ | ✅ |
| 配置文件 | ❌ | ✅ JSON |
| 热加载 | ❌ | ✅ |
| systemd | ❌ | ✅ |
| 日志文件 | ❌ | ✅ |
| 进程管理 | ❌ | ✅ |
| 白名单 | 硬编码 | ✅ 可配置 |
| 一键安装 | ❌ | ✅ |

## 📝 卸载

```bash
# 1. 停止服务
mini-fail2ban stop

# 2. 禁用自启
mini-fail2ban disable

# 3. 删除文件
sudo rm -rf /opt/mini-fail2ban
sudo rm -rf /etc/mini-fail2ban
sudo rm /etc/systemd/system/mini-fail2ban.service
sudo rm /usr/local/bin/mini-fail2ban
sudo rm /var/run/mini-fail2ban.pid
sudo rm /var/log/mini-fail2ban.log

# 4. 重载 systemd
sudo systemctl daemon-reload
```

## 📄 许可证

MIT License
