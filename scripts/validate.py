"""验证发布索引、图片摘要、来源清单与文件引用闭合。"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from sync import ROOT,DESTINATION

def validate(root):
    index=json.loads((root/'index.json').read_text())
    manifest=json.loads((root/'manifest.json').read_text())
    assert index and manifest['images']
    used=set()
    for name,url in index.items():
        parsed=urlsplit(url)
        prefix=f'/{DESTINATION}/main/logos/'
        assert name and parsed.scheme=='https' and parsed.netloc=='raw.githubusercontent.com'
        assert parsed.path.startswith(prefix) and not parsed.query and not parsed.fragment
        filename=parsed.path[len(prefix):]
        assert '/' not in filename and len(filename.split('.')[0])==64
        data=(root/'logos'/filename).read_bytes()
        assert hashlib.sha256(data).hexdigest()==filename.split('.')[0]
        used.add(filename)
    for record in manifest['images']:
        assert record['file']=='logos/'+record['sha256']+Path(record['file']).suffix
        assert record['file'].split('/')[-1] in used
        assert record['name'] in index
    assert used=={p.name for p in (root/'logos').iterdir() if p.is_file()}
    print(f'验证通过：{len(index)} 个名称，{len(used)} 份图片，索引无缺失或冗余文件')

if __name__=='__main__':validate(ROOT)
