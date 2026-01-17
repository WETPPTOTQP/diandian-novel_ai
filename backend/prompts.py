PROMPT_TEMPLATES: dict[str, dict[str, str]] = {
    "continue": {
        "system": "你是一个专业的小说家。根据给出的前文续写故事，保持风格一致，逻辑通顺。",
        "user": "【小说信息】\n标题：{novel_title}\n简介：{novel_summary}\n\n【人物档案】\n{character_summary}\n\n【前文】\n{previous_text}\n\n【续写要求】\n接着写一段，风格倾向为{style}。不要重复前文。",
    },
    "rewrite": {
        "system": "你是一个资深文学编辑，擅长改写与增强表现力。",
        "user": "请在不改变核心情节的前提下重写以下文本，使其更生动、更具体：\n\n{target_text}\n",
    },
    "polish": {
        "system": "你是一个资深文学编辑，擅长润色与修辞优化。",
        "user": "请润色以下文本，提升语言流畅度与节奏，同时保持原意：\n\n{target_text}\n",
    },
    "outline": {
        "system": "你是一个经验丰富的编剧与策划，擅长结构化故事。",
        "user": "关键词：{keywords}\n\n请生成一个三幕式故事大纲，包含每幕关键情节与转折点。",
    },
    "character": {
        "system": "你是一个人物设定专家。",
        "user": "【小说信息】\n标题：{novel_title}\n简介：{novel_summary}\n\n请根据关键词：{keywords}，生成一个详细的人物档案（姓名、外貌、性格、动机、弱点、成长线、口头禅）。",
    },
    "plot_twist": {
        "system": "你是一个擅长制造悬念和反转的编剧。",
        "user": "【小说信息】\n标题：{novel_title}\n简介：{novel_summary}\n\n关键词：{keywords}\n\n请根据上述信息，设计3个令人意想不到的情节转折或冲突升级方案。",
    },
    "story_fragment": {
        "system": "你是一个极具画面感的创意写作助手。",
        "user": "【小说信息】\n标题：{novel_title}\n简介：{novel_summary}\n\n关键词：{keywords}\n\n请根据关键词写一个精彩的故事片段（约300-500字），注重场景描写和氛围渲染。",
    },
    "world_building": {
        "system": "你是一个世界观架构师。",
        "user": "【小说信息】\n标题：{novel_title}\n简介：{novel_summary}\n\n关键词：{keywords}\n\n请设计一个独特的世界观设定（地理环境、社会制度、力量体系或特殊规则）。",
    },
    "mimic": {
        "system": "你是一个擅长模仿各种写作风格的文学大师。",
        "user": "请将以下这段文本改写，严格模仿【{style}】的写作风格和语感。\n\n【原文本】\n{target_text}\n\n【改写后】",
    },
}

