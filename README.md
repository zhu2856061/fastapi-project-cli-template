
## 项目整体结构
.
├── LICENSE
├── README.md
├── config.yaml
├── dockerfile
├── gunicorn_conf.py
├── logging.ini
├── main.py
├── makefile
├── pyproject.toml
├── scripts
│   └── run.sh
├── src
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── routers
│   │       │   ├── __init__.py
│   │       │   ├── chatbot_router.py
│   │       │   └── vector_router.py
│   │       └── schemas
│   │           ├── __init__.py
│   │           ├── chatbot_schema.py
│   │           └── vector_schema.py
│   ├── clients
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── app_config.py
│   │   └── logging_config.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── chatbot
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── constants.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── exceptions.py
│   │   │   └── security.py
│   │   └── vector
│   │       ├── __init__.py
│   │       ├── constants.py
│   │       ├── database.py
│   │       ├── dependencies.py
│   │       ├── exceptions.py
│   │       ├── security.py
│   │       └── vector_model.py
│   ├── exceptions
│   │   └── app_exception.py
│   ├── middleware
│   │   ├── __init__.py
│   │   └── super_agent_hooks.py
│   ├── models
│   │   └── __init__.py
│   ├── repositories
│   │   └── __init__.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── chatbot_service.py
│   │   └── vector_service.py
│   └── utils
│       ├── __init__.py
│       ├── common.py
│       └── decorators.py
└── tests
    └── test_client.py


## 项目详细拆解

### 统一日志管理

**需要修改点**: `script/run.sh`文件中设置环境变量 WORK_ENV=dev/prod

##### 核心文件：logging.ini & src/vector_service/core/config/logging_config.py

**logging.ini** 文件 涉及三个字段：loggers， handlers， formatters
[loggers]    # 日志的【使用者】：谁在打日志
相当于你在给系统报名单：
“我要监控这些模块的日志 ——root、chatbot、uvicorn、sqlalchemy、httpx...”
[handlers]   # 日志的【输出方式】：日志打印到哪里
console：输出到控制台（黑窗口）
rotating_file：输出到日志文件，并自动按天切割
[formatters] # 日志的【格式】：日志长什么样

**logging_config.py** 文件
该文件的核心是：init_app_logging(*, json_logs=True, log_level: str = "INFO")
json_logs=True 时输出纯 JSON（生产环境）
json_logs=False 时输出彩色控制台日志（开发环境）

**使用方法**: 将在main.py 中使用 init_app_logging初始化即可，通过环境变量 `WORK_ENV` 来判断是开发环境 `dev` 还是生产环境 `prod`，从而获得不一样日志输出样式，通过在`script/run.sh`中设置环境变量 WORK_ENV=dev/prod


### 统一配置管理

**需要修改点**: `config.yaml`文件中除`SYSTEM`字段外的其他所有字段

##### 核心文件：config.yaml & src/vector_service/core/config/app_config.py
**config.yaml** 文件 `SYSTEM` 字段是系统核心字段，其他字段随心所配
**app_config.py** 文件 与`config.yaml` 文件对应，其中 SystemConfig 和 AppConfig 类是核心类，不可修改名字

**使用方法**: 将在 main.py 中使用 init_app_config 初始化即可，通过环境变量：`CONFIG_PATH` 和 `ENV_PATH` 来获得不同环境配置（环境变量覆盖基础配置），通过在`script/run.sh`中设置环境变量，在其他模块中调用时，采用 get_app_config() 获得配置


### 统一异常管理

**需要修改点**: `src/vector_service/core/exceptions.py`文件中除`AppException`字段外的其他字段

##### 核心文件：src/vector_service/core/exceptions.py & main.py
**exceptions.py** 文件 自定义异常类都需要继承 AppException
**main.py** 文件 定义4层异常处理器（捕获所有 Exception）



### 统一监控管理

**需要修改点**: `src/vector_service/utils/decorators.py`文件，所有的监控行为只能通过装饰器采用零侵入模式


### 统一部署框架

##### 核心文件：gunicorn_conf.py & dockerfile & makefile

**gunicorn_conf.py** 文件， 几乎不用修改，与config.yaml 文件呼应

**makefile** 文件，make build 将编译你的src文件，并打包tar.gz；编译完成后，make release 将构建服务镜像，该文件将承接所有命令操作（你若是经常执行某个命令，就将其加入其中）

**dockerfile** 文件，镜像构建文件，里面大部分不可修改，留意文件内的最下部分【核心修改带】，这里就是你的操作空间


### 其他代码规范注意项
- alembic / alembic.ini db迁移能力，当你业务场景中添加了数据库字段，请使用 alembic 迁移能力, 没用该能力的时候，请保持上述两个文件不变（不建议删除）
- pyproject.toml 文件里面，[tool.**]内的内容不允许修改，这个是保持代码风格一致
- makefile 文件，主要是加入一些常用命令和用于[核心]编译整个项目的命令
- LICENSE 文件，请保持不变，MIT
- .gitignore 文件，请保持不变，有特殊需求时，请自行添加到文档最后一行
- scripts 文件夹，存放一些脚本，如：run.sh
- tests 文件夹，存放测试用例
- src 文件夹，存放项目核心代码


## 使用说明

1.  保持代码结构一致
2.  开发过程中安装库，请采用uv add XXX，若是有自己的pyproject.oml文件，则使用make sync 一次性同步安装
3.  开发阶段使用scripts 内的sh run.sh 脚本进行启动服务，采用tests内的脚本进行本地测试
4.  开发完成后，进行部署，采用统一部署框架
