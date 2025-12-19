from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import time
import os
import random

app = Flask(__name__)

# 允许前端跨域访问所有接口，如需收紧可改为 resources={r"/api/*": {"origins": "你的前端域名"}}
CORS(app)

# ================= 配置区（上线时用环境变量注入密钥） =================
# 优先从环境变量读取，如果没有则尝试从本地配置文件读取（仅用于本地测试）
SERPER_KEY = os.getenv("SERPER_KEY", "")
GROQ_KEY = os.getenv("GROQ_KEY", "")

# 如果环境变量为空，尝试从本地配置文件读取（仅用于本地开发）
if not SERPER_KEY or not GROQ_KEY:
    try:
        from config_local import SERPER_KEY as LOCAL_SERPER_KEY, GROQ_KEY as LOCAL_GROQ_KEY
        if not SERPER_KEY:
            SERPER_KEY = LOCAL_SERPER_KEY
        if not GROQ_KEY:
            GROQ_KEY = LOCAL_GROQ_KEY
        print("[INFO] 已从 config_local.py 读取密钥（仅用于本地开发）")
    except ImportError:
        pass  # 如果没有 config_local.py，继续使用环境变量（空字符串）
# =================================================================

# ================= 全量来源库（25+ 个来源） =================
ALL_SOURCES = [
    "网页", "知乎", "豆瓣", "小红书", "公众号", "微博", "贴吧", 
    "抖音", "快手", "本地", "地方志", "地图", "学术", "音乐", 
    "B站", "点评", "美团", "旅行", "播客", "新闻", "资讯", 
    "澎湃", "国家地理", "博物馆", "艺术"
]
# =================================================================

def get_ai_insight(city, contexts, selected_sources):
    """调用 Groq Llama 3.1 生成城市侧写"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    # 动态生成 Prompt，告诉 AI 选中的 6 个维度
    sources_str = "、".join(selected_sources)
    prompt = f"""你是一位博学且优雅的旅行家，正在对【{city}】进行深度解构。你的使命是：拨开时代烟尘，触碰这座城市最深处的灵魂。

你现在选中的 6 个维度是：{sources_str}。请严格按照这 6 个平台的风格分别写一段解构文案。

写作要求：
1. **开头必须是一段充满画面感、充满人文温情的引言**（50-80字）
   - 不要直接罗列数据或事实
   - 用细腻的笔触描绘这座城市给你的第一印象
   - 可以是清晨的街景、黄昏的市井、夜晚的灯火，或是某个瞬间的触动
   - 让读者仿佛能看见、听见、感受到这座城市的气息

2. **主体部分**（70-100字）
   - 用散文化的优美段落展开，严禁使用生硬的列表格式
   - 像在讲述一个故事，而不是在做报告
   - 挖掘这座城市在历史长河中的沉淀，以及当下最真实的生活肌理
   - 可以穿插历史脉络、文化底蕴、人文风情，但要用文学化的语言串联
   - 参考这 6 个维度（{sources_str}）的不同视角和风格，让文字更丰富多元

3. **结尾**（20-30字）
   - 一句意味深长的感悟或建议
   - 不要显得刻意或说教，要自然流露

整体风格：
- 语气像一位博学且优雅的旅行家，正在对一座古城进行深度解构
- 文字要有温度、有画面感、有文学质感
- 避免生硬的列举、数据堆砌、模板化表达
- 多用散文化的优美段落，让文字流淌出诗意

参考信息（仅供参考，不必全部使用，融入你的文字中）：
{contexts}

现在，请开始你的城市解构之旅："""
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # 使用新的模型，如果不行可以尝试 "llama-3.1-8b-instant"
        "messages": [
            {"role": "system", "content": "你是一位博学且优雅的旅行家，擅长用充满画面感和人文温情的文字解构城市。你的文字像散文一样优美，有温度、有深度，能拨开时代烟尘，触碰城市最深处的灵魂。你从不使用生硬的列表格式，而是用散文化的段落娓娓道来，让读者仿佛置身其中，感受到城市的呼吸与脉搏。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85  # 提高温度值，让回复更有创意和文学性
    }
    
    # 关键配置检查
    if not GROQ_KEY:
        print("Groq API Key 未配置，请设置环境变量 GROQ_KEY")
        return "后端密钥未配置，暂时无法生成城市侧写，请联系管理员。"

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        response_data = res.json()
        
        # 提取 AI 生成的内容
        ai_content = response_data['choices'][0]['message']['content']
        print(f"[DEBUG] Groq API 返回的完整内容: {ai_content}")
        print(f"[DEBUG] Groq API 返回内容长度: {len(ai_content)}")
        
        # 清理内容：移除可能的提示性语言
        cleaned_content = ai_content.strip()
        
        # 如果内容包含提示性语言，尝试提取真正的介绍部分
        if "✨" in cleaned_content or "AI 已深入检索" in cleaned_content or "为你呈现" in cleaned_content or "文化切片" in cleaned_content:
            print(f"[WARNING] 检测到提示性语言，尝试清理...")
            # 移除包含提示性语言的行
            lines = cleaned_content.split("\n")
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # 跳过包含提示性语言的行
                if "✨" in line or "AI 已深入检索" in line or "为你呈现" in line or "文化切片" in line:
                    continue
                # 如果行中包含冒号，尝试提取冒号后的内容
                if "：" in line:
                    line = line.split("：", 1)[-1].strip()
                elif ":" in line:
                    line = line.split(":", 1)[-1].strip()
                if line and len(line) > 5:  # 只保留有意义的行
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                cleaned_content = "\n".join(cleaned_lines).strip()
            else:
                # 如果清理后没有内容，尝试从原文中提取
                # 查找第一个句号后的内容
                if "。" in cleaned_content:
                    parts = cleaned_content.split("。")
                    cleaned_content = "。".join([p for p in parts if "✨" not in p and "AI" not in p[:10]]) + "。"
                elif "." in cleaned_content:
                    parts = cleaned_content.split(".")
                    cleaned_content = ".".join([p for p in parts if "✨" not in p and "AI" not in p[:10]]) + "."
        
        # 确保返回的是真正的总结内容，而不是提示信息
        if cleaned_content and len(cleaned_content.strip()) > 20:
            print(f"[DEBUG] 清理后的内容: {cleaned_content[:100]}...")
            return cleaned_content
        else:
            print(f"[WARNING] Groq API 返回内容过短或为空")
            return f"{city}是一座充满历史底蕴的城市，这里有着独特的文化魅力和人文风情。漫步街头，你能感受到这座城市在时光流转中沉淀下来的独特韵味。"
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Groq API 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return "城市档案正在加密重组中，请先行查阅下方碎片..."
    except Exception as e:
        print(f"[ERROR] Groq API 处理错误: {e}")
        import traceback
        traceback.print_exc()
        return "城市档案正在加密重组中，请先行查阅下方碎片..."

@app.route("/", methods=["GET"])
def index_root():
    """根路径：返回前端 HTML 页面"""
    return send_from_directory('.', 'Index.html')


@app.route("/health", methods=["GET"])
def health_check():
    """简单健康检查，方便部署平台探活"""
    return jsonify({"status": "ok"})

@app.route("/api/health", methods=["GET"])
def api_health_check():
    """API 健康检查端点，返回详细状态信息"""
    return jsonify({"status": "ok", "message": "AI City backend is running"})

@app.route("/api/test", methods=["GET"])
def test_api():
    """测试接口，返回固定格式的数据"""
    return jsonify({
        "city": "测试城市",
        "summary": "这是一个测试总结，用于验证前端能否正确接收 summary 字段。",
        "results": [
            {
                "title": "测试标题",
                "link": "#",
                "snippet": "测试描述",
                "source": "测试来源"
            }
        ]
    })


@app.route("/api/search", methods=["POST"])
def handle_search():
    data = request.json
    city = data.get('city', '').strip()
    
    if not city:
        return jsonify({"error": "请输入有效的城市名称"}), 400

    # 1. Check Serper Key
    if not SERPER_KEY:
        return jsonify({"error": "后端密钥未配置，请联系管理员配置 SERPER_KEY"}), 500

    # 2. 随机抽取 6 个完全不同的来源（打破来源局限）
    selected_sources = random.sample(ALL_SOURCES, min(6, len(ALL_SOURCES)))
    print(f"[DEBUG] 随机抽取的 6 个维度: {selected_sources}")
    
    # 3. 社交媒体数据检索 (Serper) - 不再硬编码来源
    search_url = "https://google.serper.dev/search"
    # 移除 site: 约束，让搜索更广泛
    query = f"{city} 深度体验 文化 历史 生活"
    
    search_headers = {
        'X-API-KEY': SERPER_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        search_res = requests.post(search_url, json={"q": query, "hl": "zh-cn"}, headers=search_headers)
        search_res.raise_for_status()  # 检查 HTTP 状态码
        search_data = search_res.json()
        organic = search_data.get('organic', [])
        
        print(f"[DEBUG] Serper 返回了 {len(organic)} 条结果")
        
        # 整理 AI 学习素材
        snippets = "\n".join([f"- {r['title']}: {r['snippet']}" for r in organic[:10]]) if organic else "暂无相关数据"
        
        # 4. 生成 AI 总结 (Groq) - 传入选中的 6 个维度
        print(f"[DEBUG] 开始调用 Groq API 生成总结...")
        try:
            ai_summary = get_ai_insight(city, snippets, selected_sources)
            print(f"[DEBUG] AI 总结生成完成，长度: {len(ai_summary) if ai_summary else 0}")
        except Exception as e:
            print(f"[WARNING] Groq API 调用失败: {e}")
            # 如果 Groq API 失败，生成一个简单的总结
            ai_summary = f"{city}是一座充满历史底蕴的城市。这里有着丰富的文化遗产和独特的人文风情，值得深入探索。"
        
        # 5. 为搜索结果分配随机抽取的来源标签
        final_results = []
        num_results = min(6, len(organic))  # 固定返回 6 个结果
        
        for i in range(num_results):
            if i < len(organic):
                item = organic[i]
                # 循环使用选中的 6 个来源
                assigned_source = selected_sources[i % len(selected_sources)]
                
                final_results.append({
                    "title": item.get('title', '无标题'),
                    "link": item.get('link', '#'),
                    "snippet": item.get('snippet', '暂无描述'),
                    "source": assigned_source
                })
        
        # 如果搜索结果不足 6 个，用占位数据补充（保持 6 个结果）
        while len(final_results) < 6:
            remaining_source = selected_sources[len(final_results) % len(selected_sources)]
            final_results.append({
                "title": f"关于{city}的{remaining_source}内容",
                "link": "#",
                "snippet": f"来自{remaining_source}的深度内容，正在整理中...",
                "source": remaining_source
            })

        response_data = {
            "city": city,
            "summary": ai_summary or "城市档案正在整理中，请查看下方搜索结果...",
            "results": final_results
        }
        
        print(f"[DEBUG] 准备返回数据，summary 字段: {response_data['summary'][:50]}...")
        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Serper API 请求失败: {e}")
        return jsonify({
            "city": city,
            "summary": "搜索服务暂时不可用，请稍后再试。",
            "results": [],
            "error": f"搜索失败: {str(e)}"
        }), 500
    except Exception as e:
        print(f"[ERROR] 系统错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "city": city,
            "summary": "系统处理出错，请稍后再试。",
            "results": [],
            "error": f"系统点火失败: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)