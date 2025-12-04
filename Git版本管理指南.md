# Git版本管理指南

## 一、初始化Git仓库

### 1. 在项目根目录初始化Git
```bash
cd E:\桌面\毕业设计
git init
```

### 2. 创建.gitignore文件（如果还没有）
确保`.gitignore`文件包含：
```
# Python
__pycache__/
*.py[cod]
venv/
venv_name/
*.egg-info/

# Node
node_modules/
dist/

# Django
*.log
db.sqlite3
/media
/static

# IDE
.vscode/
.idea/

# Environment
.env
.env.local
```

## 二、首次提交到GitHub

### 1. 在GitHub上创建新仓库
- 访问 https://github.com
- 点击右上角 "+" → "New repository"
- 填写仓库名称（如：graduation-project）
- 选择 Public 或 Private
- **不要**勾选"Initialize this repository with a README"
- 点击"Create repository"

### 2. 连接本地仓库到GitHub
```bash
# 添加所有文件到暂存区
git add .

# 提交到本地仓库
git commit -m "Initial commit: 毕业设计项目初始版本"

# 添加远程仓库（替换YOUR_USERNAME和YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 三、日常版本管理流程

### 1. 查看当前状态
```bash
# 查看哪些文件被修改了
git status

# 查看具体修改内容
git diff
```

### 2. 提交修改
```bash
# 添加修改的文件到暂存区
git add .

# 或者只添加特定文件
git add frontend/src/pages/Home.vue

# 提交到本地仓库（使用有意义的提交信息）
git commit -m "feat: 添加官方验专区和发布闲置功能

- 将相机专区改为官方验专区入口
- 添加右侧浮动发布按钮
- 优化下拉菜单样式"

# 推送到GitHub
git push
```

### 3. 提交信息规范（推荐）
使用约定式提交格式：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 四、版本标签管理（重要版本标记）

### 1. 创建版本标签
```bash
# 创建轻量标签
git tag v1.0.0

# 创建带注释的标签（推荐）
git tag -a v1.0.0 -m "版本1.0.0: 项目初始完成版本"

# 查看所有标签
git tag

# 查看标签详情
git show v1.0.0
```

### 2. 推送标签到GitHub
```bash
# 推送单个标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 3. 版本号规范（语义化版本）
格式：`主版本号.次版本号.修订号`
- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

示例：
- `v1.0.0` - 初始版本
- `v1.1.0` - 添加新功能
- `v1.1.1` - 修复bug
- `v2.0.0` - 重大更新，可能不兼容

## 五、分支管理（推荐用于重大修改）

### 1. 创建功能分支
```bash
# 创建并切换到新分支
git checkout -b feature/official-verification

# 或者使用新语法
git switch -c feature/official-verification
```

### 2. 在分支上工作
```bash
# 正常提交代码
git add .
git commit -m "feat: 添加官方验货功能"

# 推送到GitHub（首次推送需要设置上游）
git push -u origin feature/official-verification
```

### 3. 合并到主分支
```bash
# 切换回主分支
git checkout main

# 拉取最新代码
git pull origin main

# 合并功能分支
git merge feature/official-verification

# 推送到GitHub
git push origin main
```

### 4. 删除已合并的分支
```bash
# 删除本地分支
git branch -d feature/official-verification

# 删除远程分支
git push origin --delete feature/official-verification
```

## 六、查看版本历史

### 1. 查看提交历史
```bash
# 简洁版本
git log --oneline

# 详细版本
git log

# 图形化显示
git log --graph --oneline --all

# 查看特定文件的修改历史
git log -- frontend/src/pages/Home.vue
```

### 2. 在GitHub上查看
- 访问你的仓库页面
- 点击 "commits" 查看所有提交
- 点击 "releases" 查看所有标签版本
- 点击 "branches" 查看所有分支

## 七、回退到之前的版本（如果需要）

### 1. 查看提交历史
```bash
git log --oneline
```

### 2. 回退到指定版本
```bash
# 软回退（保留修改）
git reset --soft <commit-hash>

# 硬回退（丢弃修改，谨慎使用）
git reset --hard <commit-hash>

# 回退到上一个版本
git reset --hard HEAD~1
```

### 3. 创建新分支保存当前状态
```bash
# 在回退前创建备份分支
git branch backup-before-reset

# 然后再回退
git reset --hard <commit-hash>
```

## 八、完整工作流程示例

### 场景：完成一个重大功能更新

```bash
# 1. 确保主分支是最新的
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/major-update

# 3. 进行开发工作
# ... 修改代码 ...

# 4. 提交修改
git add .
git commit -m "feat: 重大功能更新

- 添加官方验专区
- 优化用户界面
- 修复已知问题"

# 5. 推送到GitHub
git push -u origin feature/major-update

# 6. 在GitHub上创建Pull Request（可选）
# 或者直接合并到主分支

# 7. 合并到主分支
git checkout main
git merge feature/major-update
git push origin main

# 8. 创建版本标签
git tag -a v1.1.0 -m "版本1.1.0: 重大功能更新"
git push origin v1.1.0

# 9. 清理分支
git branch -d feature/major-update
git push origin --delete feature/major-update
```

## 九、常见问题解决

### 1. 推送被拒绝
```bash
# 先拉取远程更改
git pull origin main

# 如果有冲突，解决冲突后
git add .
git commit -m "merge: 合并远程更改"
git push origin main
```

### 2. 忘记提交某些文件
```bash
# 修改最后一次提交
git add forgotten-file.js
git commit --amend --no-edit

# 如果已经推送，需要强制推送（谨慎使用）
git push --force origin main
```

### 3. 撤销未提交的修改
```bash
# 撤销工作区的修改
git checkout -- <file>

# 撤销所有未提交的修改
git reset --hard HEAD
```

## 十、GitHub最佳实践

1. **定期提交**：完成一个小功能就提交一次
2. **有意义的提交信息**：清楚描述做了什么
3. **使用分支**：重大功能在独立分支开发
4. **创建标签**：重要版本创建标签便于回溯
5. **编写README**：说明项目结构和运行方法
6. **使用.gitignore**：避免提交不必要的文件

## 十一、快速参考命令

```bash
# 初始化
git init
git remote add origin <url>

# 日常操作
git status              # 查看状态
git add .               # 添加所有修改
git commit -m "消息"    # 提交
git push                # 推送

# 版本管理
git tag -a v1.0.0 -m "版本说明"  # 创建标签
git push origin --tags           # 推送标签

# 分支管理
git checkout -b <分支名>  # 创建分支
git checkout <分支名>      # 切换分支
git merge <分支名>         # 合并分支

# 查看历史
git log --oneline        # 简洁历史
git log --graph --all    # 图形化历史
```

