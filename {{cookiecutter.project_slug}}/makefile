.PHONY: build sync install-torch

MODULE := src

# 项目核心编译模块
# 1 nuitka 编译
# 2 添加主要文件，pyproject.toml main.py config.yaml logging.ini
# 3 打包tar.gz 并 删除build过程文件, 方便docker镜像使用 
build:
	@echo "⏳ 开始构建..."
	rm -rf ./build
	python -m nuitka --module $(MODULE) --include-package=$(MODULE) --output-dir=./build
	cp pyproject.toml main.py gunicorn_conf.py .env config.yaml logging.ini ./build
	cd ./build && mv *.so ${MODULE}.so && tar -czvf server.tar.gz pyproject.toml main.py gunicorn_conf.py .env config.yaml logging.ini ${MODULE}.so && rm -rf pyproject.toml main.py gunicorn_conf.py .env config.yaml *.build *.pyi logging.ini ${MODULE}.so
	@echo "✅ 构建完成！核心文件：server.tar.gz"

# uv 普通同步
sync:
	UV_LINK_MODE=copy UV_TORCH_BACKEND=auto uv sync

# uv torch添加，主要是单独添加torch，自动GPU / CPU，比如本地电脑没有GPU，就没必要安装GPU版（太大了）
install-torch:
	UV_LINK_MODE=copy UV_TORCH_BACKEND=auto uv add torch

release:
	@echo "⏳ 开始构建镜像..."
	docker build -f dockerfile -t {{ cookiecutter.author_name }}/{{ cookiecutter.project_slug }}:{{ cookiecutter.version }} .
	@echo "✅ 构建完成！镜像：{{ cookiecutter.author_name }}/{{ cookiecutter.project_slug }}:{{ cookiecutter.version }}"