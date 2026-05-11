提交包说明

包含文件：
- 源码/main.py
- 实验结果/Res.txt
- 实验报告/报告.txt
- 可执行文件/说明.txt

请确保在解压后将 `main.py` 放在同一目录下并使用 `python3 main.py` 运行。

可执行文件和构建说明：
- 在 `可执行文件` 目录下已经提供两个脚本：
	- `run.sh`：直接使用系统 `python3` 运行 `main.py` 的快捷脚本（确保 Python3 在 PATH 中）。
	- `build_executable.sh`：使用 `PyInstaller` 构建独立可执行文件（one-file）。

构建独立可执行文件示例：
1. 确保系统安装了 `python3`。
2. 运行：
```bash
cd 可执行文件
./build_executable.sh
```
构建完成后，最终的可执行文件会放在 `可执行文件/dist/` 下（在 macOS/Linux 上名为 `PageRank`，在 Windows 上为 `PageRank.exe`）。

注意：`build_executable.sh` 会在本地创建临时虚拟环境并安装 `pyinstaller` 以及 `源码/requirements.txt` 中列出的包，请在网络可用时运行。
