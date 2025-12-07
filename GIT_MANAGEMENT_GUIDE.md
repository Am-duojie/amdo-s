# Git 项目管理指南

## 📋 当前项目状态

- **本地分支**: main
- **远程仓库**: https://github.com/Am-duojie/amdo-s
- **当前状态**: 有 60+ 个未提交的修改

## 🔧 日常开发工作流

### 1. 开始工作前

```powershell
# 拉取最新代码
git pull origin main

# 查看当前状态
git status
```

### 2. 提交代码的标准流程

```powershell
# 1. 查看修改的文件
git status

# 2. 添加要提交的文件（推荐分批次提交）
git add <文件路径>              # 添加单个文件
git add <目录路径>              # 添加整个目录
git add .                      # 添加所有修改（谨慎使用）

# 3. 提交更改
git commit -m "描述性的提交信息"

# 4. 推送到远程仓库
git push origin main
```

### 3. 提交信息规范

使用清晰、描述性的提交信息：

```
✅ 好的提交信息：
- "修复支付回调地址配置问题"
- "添加用户认证功能"
- "优化商品列表加载性能"
- "修复分账模式bug，完善易淘业务流程"

❌ 不好的提交信息：
- "更新"
- "修复bug"
- "修改"
```

### 4. 查看和比较更改

```powershell
# 查看未暂存的更改
git diff

# 查看已暂存的更改
git diff --staged

# 查看提交历史
git log --oneline -10

# 查看某个文件的修改历史
git log --oneline <文件路径>
```

## 🚨 常见场景处理

### 场景1: 撤销未提交的更改

```powershell
# 撤销单个文件的修改（未添加到暂存区）
git restore <文件路径>

# 撤销所有未提交的修改（危险操作！）
git restore .

# 撤销已添加到暂存区的文件
git restore --staged <文件路径>
```

### 场景2: 修改最后一次提交

```powershell
# 修改提交信息
git commit --amend -m "新的提交信息"

# 添加遗漏的文件到上次提交
git add <遗漏的文件>
git commit --amend --no-edit
```

### 场景3: 创建新分支进行功能开发

```powershell
# 创建并切换到新分支
git checkout -b feature/新功能名称

# 或者使用新语法
git switch -c feature/新功能名称

# 在新分支上开发完成后
git add .
git commit -m "完成新功能"
git push origin feature/新功能名称

# 切换回主分支
git checkout main
# 或
git switch main
```

### 场景4: 处理冲突

```powershell
# 拉取时如果有冲突
git pull origin main

# 手动解决冲突后
git add <解决冲突的文件>
git commit -m "解决合并冲突"
git push origin main
```

### 场景5: 查看远程仓库信息

```powershell
# 查看远程仓库
git remote -v

# 如果远程仓库配置错误，可以更新
git remote set-url origin https://github.com/Am-duojie/amdo-s.git

# 查看远程分支
git branch -r
```

## 📦 当前未提交文件的处理建议

您当前有 60+ 个未提交的文件，建议按功能模块分批提交：

### 方案1: 按文件类型分组提交

```powershell
# 1. 先提交文档类文件
git add *.md
git commit -m "更新项目文档"

# 2. 提交后端配置和脚本
git add backend/*.ps1 backend/*.py
git commit -m "更新后端配置和工具脚本"

# 3. 提交前端代码
git add frontend/src/
git commit -m "更新前端页面和组件"

# 4. 推送到远程
git push origin main
```

### 方案2: 按功能模块提交

```powershell
# 1. 支付相关功能
git add backend/ALIPAY_* backend/PAYMENT_* backend/test_payment.py
git commit -m "更新支付相关功能和文档"

# 2. ngrok 配置相关
git add backend/NGROK_* backend/ngrok* backend/*ngrok*
git commit -m "更新ngrok配置和文档"

# 3. 管理后台相关
git add frontend/src/admin/
git commit -m "更新管理后台页面"

# 4. 其他修改
git add .
git commit -m "其他功能更新"
git push origin main
```

## 🔐 重要文件管理

### 不应该提交到 Git 的文件

确保以下文件在 `.gitignore` 中（已配置）：
- `venv/` - Python 虚拟环境
- `node_modules/` - Node.js 依赖
- `db.sqlite3` - 数据库文件
- `.env` - 环境变量文件
- `*.log` - 日志文件
- `/media` - 媒体文件

### 敏感信息处理

```powershell
# 如果误提交了敏感信息，需要从历史中删除
# 这需要谨慎操作，建议先备份
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <敏感文件>" \
  --prune-empty --tag-name-filter cat -- --all
```

## 📊 定期维护

### 每周/每月检查

```powershell
# 1. 清理未跟踪的文件
git clean -n  # 预览将要删除的文件
git clean -f  # 实际删除未跟踪的文件

# 2. 查看仓库大小
git count-objects -vH

# 3. 优化仓库
git gc --prune=now
```

## 🎯 最佳实践

1. **频繁提交**: 每完成一个小功能就提交一次
2. **清晰的提交信息**: 使用中文描述，说明做了什么
3. **提交前检查**: 使用 `git status` 和 `git diff` 检查更改
4. **定期推送**: 每天结束工作前推送到远程仓库
5. **使用分支**: 开发新功能时创建新分支，完成后合并
6. **不要提交临时文件**: 确保 `.gitignore` 配置正确

## 🆘 紧急情况处理

### 如果本地代码丢失

```powershell
# 从远程仓库恢复
git fetch origin
git reset --hard origin/main
```

### 如果需要回退到某个提交

```powershell
# 查看提交历史
git log --oneline

# 回退到指定提交（保留更改）
git reset --soft <提交hash>

# 回退到指定提交（丢弃更改）
git reset --hard <提交hash>
```

## 📝 当前建议

基于您当前的状态，建议：

1. **立即操作**: 先提交当前的修改，避免丢失工作
2. **分批提交**: 按功能模块或文件类型分批提交，便于追踪
3. **检查远程**: 确认远程仓库 URL 是否正确配置
4. **建立习惯**: 每天结束工作前提交并推送代码


