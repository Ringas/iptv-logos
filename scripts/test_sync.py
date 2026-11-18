"""同步边界回归，不使用网络或真实数据。"""
import io
from pathlib import Path
import tempfile
import zipfile
from sync import build,save
from validate import validate

PNG=b'\x89PNG\r\n\x1a\nfixture'
def archive(entries,comment=b'a'*40):
    raw=io.BytesIO()
    with zipfile.ZipFile(raw,'w') as z:
        z.comment=comment
        for name,data in entries:z.writestr(name,data)
    return raw.getvalue()

raw=archive([('repo-main/CCTV1.png',PNG),('repo-main/风云剧场.png',PNG),
 ('repo-main/农林卫视.png',PNG),('repo-main/国学.png',PNG),
 ('repo-main/../bad.png',PNG),('repo-main/scripts/private.txt',b'secret')])
files,index,manifest=build(raw)
assert len(files)==1 and len(manifest['images'])==4
assert index['CCTV风云剧场']==index['风云剧场']
assert index['中国农林卫视']==index['农林卫视']
assert index['国学频道']==index['国学']
assert 'bad' not in index and not any('secret' in str(v) for v in index.values())
with tempfile.TemporaryDirectory() as d:
    root=Path(d);save(root,files,index,manifest);validate(root)
    stamps={p:p.stat().st_mtime_ns for p in root.rglob('*') if p.is_file()}
    save(root,files,index,manifest)
    assert all(p.stat().st_mtime_ns==stamp for p,stamp in stamps.items())
    (root/'logos'/'unused.png').write_bytes(PNG)
    save(root,files,index,manifest);assert not (root/'logos'/'unused.png').exists()
    before=(root/'index.json').read_bytes()
    for bad in [archive([('repo/x.png',b'bad')]),archive([('repo/README.md',b'text')]),archive([('repo/x.png',PNG)],b'invalid')]:
        try:build(bad);raise AssertionError('invalid archive accepted')
        except ValueError:pass
        assert (root/'index.json').read_bytes()==before
print('同步回归通过：安全路径、内容去重、明确别名、稳定地址、失败保留与无引用清理')
