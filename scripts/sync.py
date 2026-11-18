"""同步公开台标、去重并生成 IPTV Studio 可直接使用的 JSON 索引。"""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tempfile
from urllib.request import Request, urlopen
import zipfile

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM='vircloud/TVLogo'
DESTINATION='Ringas/iptv-logos'
LIMIT=32*1024*1024

# Only confirmed names; never guess similar channel names or merge language editions.
ALIASES={
 'CCTV4K超高清':'CCTV4K','CCTV8K超高清':'CCTV8K',
 'CGTN西班牙语':'CGTN西语','CGTN阿拉伯语':'CGTN阿语',
 '中国农林卫视':'农林卫视','国学频道':'国学',
 '凤凰中文':'凤凰卫视中文台','凤凰资讯':'凤凰卫视资讯台',
 'RTHK31':'RTHKTV31.hk','RTHK32':'RTHKTV32.hk',
 'CCTV央视文化精品':'文化精品','CCTV央视台球':'央视台球',
 'CCTV高尔夫·网球':'高尔夫网球',
}
for title in ('风云剧场','怀旧剧场','世界地理','风云音乐','兵器科技',
              '风云足球','女性时尚','电视指南','卫生健康'):
 ALIASES['CCTV'+title]=title

def build(raw):
    files={};index={};records=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
        revision=bundle.comment.decode('ascii')
        if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('归档缺少有效版本')
        entries=bundle.infolist()
        if len(entries)>20000:raise ValueError('仓库文件过多')
        total=0
        for entry in sorted(entries,key=lambda e:e.filename):
            path=PurePosixPath(entry.filename)
            if entry.is_dir() or len(path.parts)!=2 or '..' in path.parts:continue
            ext=path.suffix.lower()
            if ext not in ('.png','.jpg','.jpeg','.webp'):continue
            if not 0<entry.file_size<=4*1024*1024:raise ValueError('图片大小异常')
            total+=entry.file_size
            if total>128*1024*1024:raise ValueError('图片总量超过限制')
            image=bundle.read(entry)
            valid=(image.startswith(b'\x89PNG\r\n\x1a\n') if ext=='.png' else
                   image.startswith(b'\xff\xd8\xff') if ext in ('.jpg','.jpeg') else
                   image.startswith(b'RIFF') and image[8:12]==b'WEBP')
            if not valid:raise ValueError('图片格式无效：'+path.name)
            digest=hashlib.sha256(image).hexdigest()
            name=digest+ext;files[name]=image
            index[path.stem]=f'https://raw.githubusercontent.com/{DESTINATION}/main/logos/{name}'
            records.append({'name':path.stem,'upstream_path':path.name,'file':'logos/'+name,'sha256':digest})
    if not index:raise ValueError('未找到台标，保留旧索引')
    for alias,target in ALIASES.items():
        if target in index:index.setdefault(alias,index[target])
    manifest={'upstream':UPSTREAM,'revision':revision,'images':records}
    return files,dict(sorted(index.items())),manifest

def save(root,files,index,manifest):
    # Validate everything first; a failed download/parse leaves the old snapshot intact.
    folder=root/'logos';folder.mkdir(exist_ok=True)
    for name,data in files.items():
        dest=folder/name
        if not dest.exists() or dest.read_bytes()!=data:dest.write_bytes(data)
    for name,value in [('index.json',index),('manifest.json',manifest)]:
        encoded=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
        dest=root/name
        if not dest.exists() or dest.read_bytes()!=encoded:
            with tempfile.NamedTemporaryFile(dir=root,delete=False) as temp:
                temp.write(encoded);tmp=Path(temp.name)
            tmp.replace(dest)
    for old in folder.iterdir():
        if old.is_file() and old.name not in files:old.unlink()

def main():
    url=f'https://codeload.github.com/{UPSTREAM}/zip/refs/heads/main'
    with urlopen(Request(url,headers={'User-Agent':'iptv-logos-sync'}),timeout=60) as response:
        raw=response.read(LIMIT+1)
    if len(raw)>LIMIT:raise ValueError('归档超过 32 MiB，保留旧快照')
    files,index,manifest=build(raw)
    save(ROOT,files,index,manifest)
    print(f'同步完成：{len(manifest["images"])} 张台标，{len(files)} 份去重图片，{len(index)} 个名称；版本 {manifest["revision"][:12]}')

if __name__=='__main__':main()
