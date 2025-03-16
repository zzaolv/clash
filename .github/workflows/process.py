import requests
import os
import json

def convert_github_url(url):
    """将 GitHub blob URL 转换为 raw URL"""
    if "github.com" in url and "/blob/" in url:
        # 替换域名
        url = url.replace("github.com", "raw.githubusercontent.com")
        # 替换 /blob/ 为 /
        url = url.replace("/blob/", "/")
        #添加 /refs/heads/
        parts = url.split("/")
        if len(parts) > 5:
            commit_sha_or_branch = parts[5]
            #删除 sha 或 分支名
            parts.pop(5)
            #将修改后的部分重新组装
            url = "/".join(parts)
            url = url.replace(f"/{commit_sha_or_branch}/", f"/refs/heads/{commit_sha_or_branch}/")
        return url
    return url

def download_and_process(url):
    """下载 URL 内容并去除以 # 开头的行"""
    # 首先转换 URL
    url = convert_github_url(url)
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出异常
        lines = response.text.splitlines()
        filtered_lines = [line for line in lines if not line.startswith('#')]
        return "\n".join(filtered_lines)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading from {url}: {e}")
        return None

def main():
    """主函数"""
    url_groups_str = os.environ.get('URL_GROUPS')
    if not url_groups_str:
        print("Error: URL_GROUPS environment variable not set.")
        return

    try:
        url_groups = json.loads(url_groups_str)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in URL_GROUPS.")
        return

    for group in url_groups:
        combined_content = []
        for url in group['urls']:
            content = download_and_process(url)
            if content:
                combined_content.append(content)

        if combined_content:
            with open(group['output'], 'w') as outfile:
                outfile.write("\n".join(combined_content))
            print(f"Processed and saved to {group['output']}")

if __name__ == "__main__":
    main()