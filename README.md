# IPTV 台标订阅

独立同步公开台标，生成可直接添加到 IPTV Studio 的 JSON 订阅。应用无需访问 GitHub 目录接口，也无需增加依赖。

订阅地址：

```text
https://raw.githubusercontent.com/Ringas/iptv-logos/main/index.json
```

在 IPTV Studio 的「源管理 → 添加订阅」选择「台标 · JSON」，填入上述地址。保存后自动更新。资料优先级数值越小越优先；未匹配或图片失效时，沿用应用的其他台标候选与原订阅台标兜底。

图片来自 [vircloud/TVLogo](https://github.com/vircloud/TVLogo)。保留原始图片，不在同步时执行美化；外观处理由应用设置决定。按文件名生成名称映射，并补充明确别名，例如 CCTV风云剧场、CCTV4K超高清、中国农林卫视与国学频道。不会根据相似度猜测频道。

每周一上海时间 04:20 自动检查，也可在 Actions 中手动运行「同步台标」。GitHub 定时任务可能延迟。新图片按 SHA256 内容去重；内容不变保持地址不变，内容变化生成新地址，无引用的旧图片随同步清理。失败不提交更新，订阅保留上次有效版本。`manifest.json` 记录上游版本和文件来源。

本地更新与校验（Python 3.10+，无第三方依赖）：

```sh
python3 scripts/test_sync.py
python3 scripts/sync.py
python3 scripts/validate.py
```

仓库不包含直播地址、家庭订阅、频道检测记录、账号或本地配置。图片权利归原权利人，详见 [来源与许可说明](NOTICE.md)；仓库中的 GPL-3.0 许可适用于自编同步脚本，不意味着重新授权台标图片。
