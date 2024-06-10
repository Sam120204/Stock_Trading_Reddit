import re
from git_filter_repo import Filter

def remove_secrets(commit):
    patterns = [
        (re.compile(rb'REDDIT_CLIENT_ID\s*=\s*[\'"]L5x_OBLY_HG9UxgxfOg69Q[\'"]'), b'REDDIT_CLIENT_ID = "REDACTED"'),
        (re.compile(rb'REDDIT_SECRET\s*=\s*[\'"]3f2igWO4Hdcu404B3KxVV81nE_hnsA[\'"]'), b'REDDIT_SECRET = "REDACTED"'),
        (re.compile(rb'REDDIT_PASSWORD\s*=\s*[\'"]curry666666[\'"]'), b'REDDIT_PASSWORD = "REDACTED"'),
        (re.compile(rb'OPENAI_API_KEY\s*=\s*[\'"]sk-proj-7zP5agloiE5C3Rt4zUPCT3BlbkFJ6XYYYFyRZD2rD2LjNP1e[\'"]'), b'OPENAI_API_KEY = "REDACTED"'),
        (re.compile(rb'MONGO_PASSWORD\s*=\s*[\'"]Zjy2022@00[\'"]'), b'MONGO_PASSWORD = "REDACTED"'),
        (re.compile(rb'NEWSAPI_KEY\s*=\s*[\'"]7f36230ffc9a4508a8509a84404ba110[\'"]'), b'NEWSAPI_KEY = "REDACTED"'),
    ]

    for blob in commit.file_changes.values():
        if blob.filename.endswith(b'config.py'):
            content = blob.data
            for pattern, replacement in patterns:
                content = pattern.sub(replacement, content)
            blob.data = content

filter = Filter(modify_commit_message=None, modify_commit=remove_secrets)
filter.run()
