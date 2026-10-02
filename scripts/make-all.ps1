# iskill-app-icon · Windows 入口（PowerShell 薄壳）
#
# 用法（PowerShell 里）：
#   .\make-all.ps1 --glyph whale --color '#10C8A1' --outdir public --name "我的应用" --sheet
#
# ⚠️ Windows 上双击 .ps1 默认是打开记事本，不是执行。要「双击就跑」用同目录的 make-all.cmd。
#
# ⚠️ 本文件必须带 UTF-8 BOM，否则 Windows PowerShell 5.1 会按 ANSI(GBK) 解码，中文提示全变乱码。
#    本文件已带 BOM（首字节 EF BB BF）。
#
# 真逻辑在 scripts\make_all.py（三平台同一份代码）。这里只做「找解释器 → 转参数」。

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"
$SkillDir = $PSScriptRoot

function Find-Python {
    # 1) 环境变量显式指定
    if ($env:ISKILL_PYTHON -and (Test-Path $env:ISKILL_PYTHON)) { return $env:ISKILL_PYTHON }
    # 2) py -3（Windows 官方启动器，最可靠）
    #    ⚠️ 不能优先用 PATH 里的 python —— 它常常是 Microsoft Store 的别名（一跑就开商店）
    $pyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $exe = & $pyLauncher.Source -3 -c "import sys;print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
    }
    # 3) PATH 里的 python / python3
    foreach ($name in @("python", "python3")) {
        $c = Get-Command $name -ErrorAction SilentlyContinue
        if ($c) { return $c.Source }
    }
    # 4) 常见安装位置兜底
    foreach ($guess in @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python313\python.exe")) {
        if (Test-Path $guess) { return $guess }
    }
    return $null
}

$py = Find-Python
if (-not $py) {
    Write-Host ""
    Write-Host "找不到 Python 3。" -ForegroundColor Red
    Write-Host "  · 先跑：winget install -e --id Python.Python.3.13"
    Write-Host "  · 或 https://www.python.org/downloads/windows/ （安装时勾选 Add python.exe to PATH）"
    Write-Host ""
    Read-Host "按回车键关闭窗口"
    exit 1
}

$script = Join-Path $SkillDir "make_all.py"
& $py $script @args
$rc = $LASTEXITCODE

# 双击 .cmd 起来的窗口：脚本一结束窗口就关，这里停一下让人看清结果。
if ($args.Count -eq 0) {
    Write-Host ""
    Read-Host "按回车键关闭窗口"
}
exit $rc
