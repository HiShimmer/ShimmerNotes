# 介绍
李宜航，Shimmer，リギコウ，你如阳光<br>
日留水硕研一，种种原因于2026年3月10日开始创建个人网站。

本站点是个人（注意断句）搭建的知识库与笔记站点，主要Computer Science学习内容、日记与杂记。

内容以 Markdown 为源，使用 Docsify 渲染，Codex直接编码，作者稍作修改，让我们感谢artificial intelligence。

## Docsify使用方式
- MarkDown官方支持文档 [在这儿](https://markdown.com.cn/)
- Docsify官方支持文档 [在这儿](https://docsify.js.org/#/zh-cn/ "click,hurry up")
- 本地编辑 Markdown，然后 git 提交并推送到 GitHub。
- 本地服务器测试,powershell中启动
  `docsify serve docs`  
默认会在 http://localhost:3000 预览
- 提交到GitHub并同步<br>
  `git add`  
  `git commit -m "update notes"`  
  `git push`  
注意事项：git push失败时可能git push 失败：Connection was reset
这是网络连接被重置，通常是网络/代理/防火墙导致
- 
如果在使用代理，配置给Git：<br>

` git config --global http.proxy http://127.0.0.1:PORT`<br>
` git config --global https.proxy http://127.0.0.1:PORT`<br>
注：具体端口查看代理APP的PORT，大部分代理端口号默认为7890

或者使用SSH(暂定)

~~- 需要生成标签与双向链接时运行：`python scripts/generate_kb.py`~~

## 入口
- [学习](Study_forever)
- [LLM](llm/index.md)
- [NLP](nlp/index.md)
- [日记](diary/index.md)
- [杂记](notes/index.md)
- [旧笔记](oldnotes/index.md)
- [标签](tags/index.md)

Tags: home
<!-- backlinks:start -->
## Backlinks
- [LLM](llm/index.md)
- [NLP](nlp/index.md)
- [日记](diary/index.md)
- [旧笔记](oldnotes/index.md)
- [杂记](notes/index.md)
<!-- backlinks:end -->
