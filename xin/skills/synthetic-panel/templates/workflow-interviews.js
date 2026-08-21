export const meta = {
  name: 'synthetic-panel-interviews',
  description: 'SSR 合成消费者访谈 fan-out：每 agent 代入一批 persona 写质性购买感想',
  phases: [{ title: 'Interview', detail: 'N agents × batch_size personas，产物写文件' }],
}
// args: { brief, outDir, model?, batches?: [{id, file}] } 或简写 { batchesDir, count }（生成 batch-001..batch-NNN）
// 防御：部分版本 harness 把 args 注入为 JSON 字符串；args 只读，一律解析/复制到本地变量
const cfg = typeof args === 'string' ? JSON.parse(args) : (args || {})
let batches = Array.isArray(cfg.batches) && cfg.batches.length ? cfg.batches : null
if (!batches && cfg.batchesDir && cfg.count) {
  batches = Array.from({ length: cfg.count }, (_, i) => {
    const id = `batch-${String(i + 1).padStart(3, '0')}`
    return { id, file: `${cfg.batchesDir}/${id}.json` }
  })
}
if (!cfg.brief || !cfg.outDir || !batches || batches.length === 0) {
  throw new Error('args 需要 {brief, outDir, batches[]} 或 {brief, outDir, batchesDir, count}；实际收到 ' +
    JSON.stringify(cfg).slice(0, 300))
}
phase('Interview')
log(`访谈 fan-out：${batches.length} 批`)
const results = await parallel(batches.map(b => () =>
  agent(
    `你是消费者访谈模拟器，任务：为一批合成 persona 各写一段真实的购买意向感想。

步骤：
1. Read 产品概念文件：${cfg.brief}
2. Read 人物卡批次文件：${b.file}（JSON，含 batch_id 和 personas 数组）
3. 对 personas 数组中的**每一个** persona：完全代入其年龄/性别/地区/收入/痛点/使用场景（attrs/pains/context 字段），假设你在产品页看到上述产品概念，**价格只看该 persona 自己的 price_label 字段**。回答问题「你有多大可能购买/订阅这个产品？」——写一段 80-120 字的简体中文第一人称感想。
要求：诚实、允许尖锐批评或无感；自然提及价格相对自己预算/收入的感受；结合自身具体场景和痛点说为什么动心或不动心；禁止出现任何数字评分或"X分"字样；禁止提到自己是 AI、模拟或 persona；各 persona 的语气、句式、关注点必须有明显差异（年龄收入地区不同，说话方式就不同）。**感想文本中需要引用词语时一律用中文引号「」，绝对禁止使用英文双引号 "（会破坏 JSON 转义）**。
4. 用 Write 工具把结果写入：${cfg.outDir}/${b.id}.json
   格式（严格 JSON，UTF-8）：{"batch_id":"${b.id}","reviews":[{"persona_id":"P0001","review":"..."}, ...]}
   reviews 必须覆盖批次文件里**全部** persona 的 id，一个都不能少。
5. 最终回复只写一行：${b.id}: <数量> reviews written —— 禁止在回复中包含任何感想正文。`,
    { label: `interview:${b.id}`, phase: 'Interview', model: cfg.model || 'sonnet' }
  )
))
const ok = results.filter(Boolean).length
log(`完成 ${ok}/${batches.length} 批（覆盖率由 validate_batches.py 终审）`)
return { requested: batches.length, agent_ok: ok }
