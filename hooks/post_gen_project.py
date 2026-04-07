import sys

# 获取渲染后的值
project_name = "{{ cookiecutter.project_name }}"
author_name = "{{ cookiecutter.author_name }}"
email = "{{ cookiecutter.email }}"
project_description = "{{ cookiecutter.project_description }}"


def validate():
    # 检查必填项是否为空
    if not project_name.strip():
        print("❌ ERROR: 'project_name' 是必填项，不能为空！")
        return False

    if not author_name.strip():
        print("❌ ERROR: 'author_name' 是必填项，不能为空！")
        return False

    if not project_description.strip():
        print("❌ ERROR: 'project_description' 是必填项，不能为空！")
        return False

    if "@" not in email:
        print(f"❌ ERROR: '{email}' 不是一个有效的邮箱地址！")
        return False

    return True


if __name__ == "__main__":
    if not validate():
        # 返回非零退出码会停止创建过程并清理生成的文件夹
        sys.exit(1)
    else:
        print("✅ 项目配置校验通过！")
