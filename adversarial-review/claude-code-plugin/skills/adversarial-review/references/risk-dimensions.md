# 6 个衰减风险维度

基于经典软件工程书籍的风险分析框架。

## R1: 认知过载（Cognitive Overload）

**诊断问题**：理解这段代码需要多少脑力？

**参考来源**：
- *A Philosophy of Software Design* — John Ousterhout: "Deep modules" 提供简单接口隐藏复杂实现
- *Code Complete* — Steve McConnell: 函数应该短小，单一职责
- *Clean Architecture* — Robert C. Martin: 单一职责原则

**检测信号**：
- 函数 > 20 行
- 嵌套 > 3 层
- 参数 > 4 个
- 单个文件 > 300 行
- 圈复杂度 > 10
- 需要大量注释才能理解

**严重性判定**：
- Warning：超过任一阈值
- Critical：多个阈值同时超过

## R2: 变更传播（Change Propagation）

**诊断问题**：改一个东西会破坏多少无关的东西？

**参考来源**：
- *The Mythical Man-Month* — Fred Brooks: "第二系统效应"
- *Refactoring* — Martin Fowler: 代码坏味道中的 "Divergent Change"
- *Software Engineering at Google* — 大规模代码库的变更管理

**检测信号**：
- 修改一个文件需要同步修改多个不相关文件
- 全局状态被多处引用
- 硬编码的跨模块引用
- 缺少抽象层（直接依赖实现细节）

**严重性判定**：
- Critical：变更传播到 3+ 个不相关模块
- Warning：变更传播到 1-2 个模块

## R3: 知识重复（Knowledge Duplication）

**诊断问题**：同一个决策是否在多处表达？

**参考来源**：
- *The Pragmatic Programmer* — Hunt & Thomas: "DRY 原则"
- *Refactoring* — Martin Fowler: "Shotgun Surgery" 坏味道
- *Domain-Driven Design* — Eric Evans: 限界上下文划分

**检测信号**：
- 相同的业务规则在多处硬编码
- 重复的验证逻辑
- 复制粘贴的代码块（即使有微小差异）
- 相同的魔法数字/字符串在多处出现

**严重性判定**：
- Warning：3+ 处重复
- Critical：重复导致不一致（一处改了另一处没改）

## R4: 偶然复杂度（Accidental Complexity）

**诊断问题**：代码是否比问题本身更复杂？

**参考来源**：
- *A Philosophy of Software Design* — John Ousterhout: "偶然复杂度 vs 本质复杂度"
- *Clean Code* — Robert C. Martin: "简单是终极的复杂"
- *The Pragmatic Programmer* — "不要过度工程"

**检测信号**：
- 为不存在的需求设计的抽象
- 过度使用设计模式（策略模式包装一个 if-else）
- 过度泛化（泛型参数只有一种用法）
- 不必要的中间层

**严重性判定**：
- Warning：增加了维护成本但功能正确
- Suggestion：可以简化但不紧急

## R5: 依赖混乱（Dependency Confusion）

**诊断问题**：依赖是否沿一致方向流动？

**参考来源**：
- *Clean Architecture* — Robert C. Martin: "依赖规则"（源码依赖只能指向内部）
- *Domain-Driven Design* — Eric Evans: 分层架构
- *Software Engineering at Google* — 依赖管理策略

**检测信号**：
- 循环依赖（A 依赖 B，B 依赖 A）
- 上层模块导入下层实现细节
- 基础设施代码渗透到业务逻辑
- 测试代码依赖生产代码的内部实现

**严重性判定**：
- Critical：循环依赖
- Warning：依赖方向不一致

## R6: 领域模型失真（Domain Model Distortion）

**诊断问题**：代码是否忠实地代表了领域？

**参考来源**：
- *Domain-Driven Design* — Eric Evans: 通用语言、限界上下文
- *Clean Architecture* — Robert C. Martin: 实体层应该反映业务规则
- *The Mythical Man-Month* — Fred Brooks: 概念完整性

**检测信号**：
- 贫血领域模型（数据对象 + 外部服务操作它们）
- 领域概念命名不当（用技术术语而非业务术语）
- 业务规则散落在服务层而非实体中
- 领域对象承担了不属于它的职责

**严重性判定**：
- Warning：模型不完美但功能正确
- Critical：模型失真导致业务逻辑错误
