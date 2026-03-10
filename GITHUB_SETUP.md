# GitHub 仓库设置指南

## 📦 项目结构

```
mini-fail2ban/
├── mini_fail2ban_daemon.py    # 主程序
├── config.json                 # 配置文件示例
├── mini-fail2ban.service       # systemd 服务文件
├── install.sh                  # 安装脚本
├── build-deb.sh               # DEB 包构建脚本
├── test-package.sh            # 包测试脚本
├── README.md                  # 项目文档
├── LICENSE                    # MIT 许可证
├── CONTRIBUTING.md            # 贡献指南
├── PACKAGING.md               # 打包说明
├── .gitignore                 # Git 忽略文件
└── GITHUB_SETUP.md           # 本文档
```

## 🚀 推送到 GitHub

### 1. 初始化 Git 仓库

```bash
cd mini-fail2ban
git init
```

### 2. 添加所有文件

```bash
git add .
```

### 3. 创建首次提交

```bash
git commit -m "Initial commit: Mini Fail2Ban v1.0.0

- Lightweight SSH login protection daemon
- Hot-reload configuration support
- Systemd integration
- Debian package support
- Cross-architecture compatible"
```

### 4. 在 GitHub 创建仓库

访问 https://github.com/new 创建新仓库：
- Repository name: `mini-fail2ban`
- Description: `Lightweight SSH login protection daemon with hot-reload config`
- Public/Private: 根据需要选择
- 不要初始化 README、.gitignore 或 LICENSE（我们已经有了）

### 5. 关联远程仓库

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/mini-fail2ban.git

# 或使用 SSH（推荐）
git remote add origin git@github.com:YOUR_USERNAME/mini-fail2ban.git
```

### 6. 推送到 GitHub

```bash
# 推送主分支
git branch -M main
git push -u origin main
```

## 🏷️ 创建发布版本

### 创建标签

```bash
git tag -a v1.0.0 -m "Release v1.0.0

Features:
- SSH login failure monitoring
- Automatic IP banning with iptables
- Hot-reload configuration
- Systemd service integration
- Whitelist support (CIDR format)
- Debian package (.deb) support
- Cross-architecture compatible"

git push origin v1.0.0
```

### 在 GitHub 创建 Release

1. 访问仓库页面
2. 点击 "Releases" → "Create a new release"
3. 选择标签 `v1.0.0`
4. 填写发布说明
5. 上传构建好的 DEB 包（可选）
6. 点击 "Publish release"

## 📝 推荐的 GitHub 仓库设置

### About 部分

- **Description**: Lightweight SSH login protection daemon with hot-reload configuration
- **Website**: 你的文档网站（如果有）
- **Topics**: 
  - `fail2ban`
  - `ssh`
  - `security`
  - `iptables`
  - `python`
  - `systemd`
  - `debian`
  - `linux`

### README Badges（可选）

在 README.md 顶部添加徽章：

```markdown
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
```

## 🔄 后续更新流程

```bash
# 1. 修改代码
# 2. 提交更改
git add .
git commit -m "描述你的更改"

# 3. 推送到 GitHub
git push origin main

# 4. 创建新版本（如果需要）
git tag -a v1.0.1 -m "版本说明"
git push origin v1.0.1
```

## 📋 检查清单

推送前确认：

- [ ] 所有代码注释使用英文
- [ ] README.md 完整且清晰
- [ ] LICENSE 文件存在
- [ ] .gitignore 配置正确
- [ ] 没有敏感信息（密码、密钥等）
- [ ] 所有脚本可执行权限正确
- [ ] 测试过安装和卸载流程

## 🌟 推荐的 GitHub Actions（可选）

创建 `.github/workflows/test.yml` 进行自动化测试：

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test installation
        run: |
          sudo bash install.sh
          mini-fail2ban status || true
```

## 📞 获取帮助

如有问题，可以：
- 查看 README.md
- 查看 CONTRIBUTING.md
- 提交 Issue
- 发起 Discussion
