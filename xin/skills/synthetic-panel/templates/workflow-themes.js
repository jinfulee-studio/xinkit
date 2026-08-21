export const meta = {
  name: 'synthetic-panel-themes',
  description: 'SSR 合成面板主题提取：每个 archetype 一个评审 agent，产出购买驱动/拒绝理由/投放文案',
  phases: [{ title: 'Themes', detail: '每 archetype 1 agent，读 themes-input 写 themes/<id>.md' }],
}
// args: { brief: string, outDir: string, inputs: [{id, file}] }
// 防御：部分版本 harness 把 args 注入为 JSON 字符串；args 只读，解析到本地变量
const cfg = typeof args === 'string' ? JSON.parse(args) : (args || {})
if (!cfg.brief || !cfg.outDir || !Array.isArray(cfg.inputs) || cfg.inputs.length === 0) {
  throw new Error('args 需要 {brief, outDir, inputs[]}；实际收到 ' + JSON.stringify(cfg).slice(0, 300))
}
phase('Themes')
const results = await parallel(cfg.inputs.map(t => () =>
  agent(
    `你是消费者洞察分析师。分析一个细分人群的合成访谈语料，提炼可直接用于营销决策的洞察。

步骤：
1. Read 产品概念：${cfg.brief}
2. Read 该人群全部访谈记录（JSONL，每行含 persona_id/expected(1-5 购买意向期望分)/price_label/attrs/review）：${t.file}
3. 写分析文件到 ${cfg.outDir}/${t.id}.md，结构：
   # <人群名> 洞察
   ## 一句话判词（该人群对产品的核心态度，≤30 字）
   ## 购买驱动 Top3（每条：驱动点 + 1 句 persona 原话引文 + persona_id）
   ## 拒绝理由 Top3（同上格式；高分人群也要找出最普遍的犹豫点）
   ## 价格敏感观察（对比该人群内不同 price_label 的反应差异，引用原话）
   ## 投放文案 ×3（直接借用 persona 原话中的痛点语言改写成广告语，每条 ≤25 字，注明来源 persona_id）
要求：引文必须逐字摘自 review 字段（禁改写禁捏造）；洞察基于 expected 高低两端对比；判断要敢下结论。
4. 最终回复只写一行：${t.id}: themes written`,
    { label: `themes:${t.id}`, phase: 'Themes', model: 'opus' }
  )
))
return { requested: cfg.inputs.length, agent_ok: results.filter(Boolean).length }
