# Windows PATH 环境变量配置指南

## 方法一：图形界面配置（推荐，最简单）

### 步骤 1：打开环境变量设置

1. **右键点击"此电脑"**（或"我的电脑"）
2. 选择 **"属性"**
3. 点击左侧的 **"高级系统设置"**
4. 在弹出的"系统属性"窗口中，点击 **"环境变量"** 按钮

**或者使用快捷键**：
- 按 `Win + R` 打开运行对话框
- 输入 `sysdm.cpl` 并回车
- 点击"高级"选项卡
- 点击"环境变量"按钮

### 步骤 2：编辑 PATH 变量

1. 在"环境变量"窗口中，找到 **"系统变量"** 区域（下方）
2. 在变量列表中找到 **`Path`** 变量
3. 选中 `Path`，点击 **"编辑"** 按钮

### 步骤 3：添加 ngrok 目录

1. 在弹出的"编辑环境变量"窗口中，点击 **"新建"** 按钮
2. 输入 ngrok.exe 所在的目录路径，例如：
   ```
   C:\ngrok
   ```
   或
   ```
   D:\Tools\ngrok
   ```
3. 点击 **"确定"** 保存

### 步骤 4：确认并应用

1. 在"编辑环境变量"窗口中点击 **"确定"**
2. 在"环境变量"窗口中点击 **"确定"**
3. 在"系统属性"窗口中点击 **"确定"**

### 步骤 5：验证配置

1. **关闭所有已打开的 PowerShell 或 CMD 窗口**（重要！）
2. 打开新的 PowerShell 或 CMD 窗口
3. 输入以下命令验证：

```powershell
ngrok version
```

如果显示版本信息，说明配置成功！

---

## 方法二：使用 PowerShell 命令行配置（快速）

### 步骤 1：打开 PowerShell（管理员权限）

1. 按 `Win + X`
2. 选择 **"Windows PowerShell (管理员)"** 或 **"终端 (管理员)"**

### 步骤 2：添加 PATH

假设 ngrok.exe 在 `C:\ngrok` 目录，运行以下命令：

```powershell
# 获取当前 PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# 添加 ngrok 目录（如果还没有）
$ngrokPath = "C:\ngrok"  # 替换为您的实际路径

if ($currentPath -notlike "*$ngrokPath*") {
    $newPath = $currentPath + ";$ngrokPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    Write-Host "✓ ngrok 路径已添加到系统 PATH" -ForegroundColor Green
} else {
    Write-Host "✓ ngrok 路径已在系统 PATH 中" -ForegroundColor Green
}
```

### 步骤 3：验证配置

关闭并重新打开 PowerShell，然后运行：

```powershell
ngrok version
```

---

## 方法三：使用 CMD 命令行配置

### 步骤 1：打开 CMD（管理员权限）

1. 按 `Win + X`
2. 选择 **"命令提示符 (管理员)"**

### 步骤 2：添加 PATH

```cmd
setx PATH "%PATH%;C:\ngrok" /M
```

**注意**：将 `C:\ngrok` 替换为您的实际路径

### 步骤 3：验证配置

关闭并重新打开 CMD，然后运行：

```cmd
ngrok version
```

---

## 常见问题

### Q1: 如何找到 ngrok.exe 的路径？

**方法 1：通过文件资源管理器**
1. 找到 ngrok.exe 文件
2. 右键点击 → 选择"属性"
3. 在"常规"选项卡中查看"位置"（就是路径）

**方法 2：如果已经解压**
- 通常解压后的目录就是路径，例如：
  - `C:\ngrok\ngrok.exe` → 路径是 `C:\ngrok`
  - `D:\Downloads\ngrok\ngrok.exe` → 路径是 `D:\Downloads\ngrok`

### Q2: 添加后仍然提示"找不到命令"

**解决方案**：
1. **关闭所有已打开的终端窗口**（重要！）
2. 重新打开 PowerShell 或 CMD
3. 如果还是不行，重启电脑

### Q3: 用户变量 vs 系统变量

- **用户变量**：只对当前用户有效
- **系统变量**：对所有用户有效（推荐）

建议使用系统变量，这样所有用户都可以使用 ngrok。

### Q4: PATH 中有多个路径，如何管理？

PATH 中的多个路径用分号（`;`）分隔，例如：
```
C:\Windows\System32;C:\Windows;C:\ngrok
```

添加新路径时，只需要在末尾添加 `;新路径` 即可。

---

## 快速验证脚本

创建一个测试脚本 `test_ngrok_path.ps1`：

```powershell
# 测试 ngrok 是否在 PATH 中
Write-Host "检查 ngrok 是否在 PATH 中..." -ForegroundColor Cyan

$paths = $env:Path -split ';'
$ngrokFound = $false

foreach ($path in $paths) {
    if (Test-Path "$path\ngrok.exe") {
        Write-Host "✓ 找到 ngrok.exe 在: $path\ngrok.exe" -ForegroundColor Green
        $ngrokFound = $true
    }
}

if (-not $ngrokFound) {
    Write-Host "✗ 未找到 ngrok.exe" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确保：" -ForegroundColor Yellow
    Write-Host "1. ngrok.exe 已解压到某个目录" -ForegroundColor White
    Write-Host "2. 该目录已添加到系统 PATH" -ForegroundColor White
    Write-Host "3. 已重新打开终端窗口" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "测试运行 ngrok..." -ForegroundColor Cyan
    try {
        $version = ngrok version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ngrok 可以正常运行" -ForegroundColor Green
            Write-Host "  版本信息: $version" -ForegroundColor Gray
        }
    } catch {
        Write-Host "✗ ngrok 无法运行: $_" -ForegroundColor Red
    }
}
```

运行测试：

```powershell
.\test_ngrok_path.ps1
```

---

## 完整配置示例

假设您将 ngrok 解压到了 `D:\Tools\ngrok`：

### 使用图形界面：

1. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
2. 在"系统变量"中找到 `Path`，点击"编辑"
3. 点击"新建"，输入：`D:\Tools\ngrok`
4. 点击"确定"保存
5. 关闭所有终端窗口
6. 重新打开 PowerShell，运行 `ngrok version` 验证

### 使用 PowerShell（管理员）：

```powershell
$ngrokPath = "D:\Tools\ngrok"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

if ($currentPath -notlike "*$ngrokPath*") {
    $newPath = $currentPath + ";$ngrokPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    Write-Host "✓ 已添加: $ngrokPath" -ForegroundColor Green
    Write-Host "请重新打开终端窗口" -ForegroundColor Yellow
} else {
    Write-Host "✓ 路径已存在" -ForegroundColor Green
}
```

---

## 总结

**最简单的步骤**：

1. 找到 ngrok.exe 所在目录（例如：`C:\ngrok`）
2. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
3. 编辑系统变量 `Path`，添加 ngrok 目录
4. **关闭所有终端窗口**
5. 重新打开 PowerShell，运行 `ngrok version` 验证

完成！现在可以在任何目录下直接使用 `ngrok` 命令了。







