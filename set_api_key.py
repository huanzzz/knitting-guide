from config import set_api_key
import getpass

def main():
    print("请输入OpenAI API密钥（输入时不会显示）：")
    api_key = getpass.getpass()
    set_api_key(api_key)
    print("API密钥已成功保存！")

if __name__ == "__main__":
    main() 