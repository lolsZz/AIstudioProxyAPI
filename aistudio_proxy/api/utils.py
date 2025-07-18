"""
API Utility Functions Module
Contains SSE generation, stream processing, token estimation, and request validation utilities
"""

import asyncio
import json
import time
import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator
from asyncio import Queue
from models import Message



# --- SSE生成函数 ---
def generate_sse_chunk(delta: str, req_id: str, model: str) -> str:
    """生成SSE数据块"""
    chunk_data = {
        "id": f"chatcmpl-{req_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}]
    }
    return f"data: {json.dumps(chunk_data)}\n\n"


def generate_sse_stop_chunk(req_id: str, model: str, reason: str = "stop", usage: dict = None) -> str:
    """生成SSE停止块"""
    stop_chunk_data = {
        "id": f"chatcmpl-{req_id}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": reason}]
    }

    # 添加usage信息（如果提供）
    if usage:
        stop_chunk_data["usage"] = usage

    return f"data: {json.dumps(stop_chunk_data)}\n\ndata: [DONE]\n\n"


def generate_sse_error_chunk(message: str, req_id: str, error_type: str = "server_error") -> str:
    """生成SSE错误块"""
    error_chunk = {"error": {"message": message, "type": error_type, "param": None, "code": req_id}}
    return f"data: {json.dumps(error_chunk)}\n\n"


# --- 流处理工具函数 ---
async def use_stream_response(req_id: str) -> AsyncGenerator[Any, None]:
    """使用流响应（从服务器的全局队列获取数据）"""
    from server import STREAM_QUEUE, clear_stream_queue, logger
    import queue

    if STREAM_QUEUE is None:
        logger.warning(f"[{req_id}] STREAM_QUEUE is None, 无法使用流响应")
        return

    logger.info(f"[{req_id}] 开始使用流响应")

    empty_count = 0
    max_empty_retries = 300  # 30秒超时
    data_received = False

    try:
        while True:
            try:
                # 从队列中获取数据
                data = STREAM_QUEUE.get_nowait()
                if data is None:  # 结束标志
                    logger.info(f"[{req_id}] 接收到流结束标志")
                    break

                # 重置空计数器
                empty_count = 0
                data_received = True
                logger.debug(f"[{req_id}] 接收到流数据: {type(data)} - {str(data)[:200]}...")

                # 检查是否是JSON字符串形式的结束标志
                if isinstance(data, str):
                    try:
                        parsed_data = json.loads(data)
                        if parsed_data.get("done") is True:
                            logger.info(f"[{req_id}] 接收到JSON格式的完成标志")
                            yield parsed_data
                            break
                        else:
                            yield parsed_data
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接返回字符串
                        logger.debug(f"[{req_id}] 返回非JSON字符串数据")
                        yield data
                else:
                    # 直接返回数据
                    yield data

                    # 检查字典类型的结束标志
                    if isinstance(data, dict) and data.get("done") is True:
                        logger.info(f"[{req_id}] 接收到字典格式的完成标志")
                        break

            except (queue.Empty, asyncio.QueueEmpty):
                empty_count += 1
                if empty_count % 50 == 0:  # 每5秒记录一次等待状态
                    logger.info(f"[{req_id}] 等待流数据... ({empty_count}/{max_empty_retries})")

                if empty_count >= max_empty_retries:
                    if not data_received:
                        logger.error(f"[{req_id}] 流响应队列空读取次数达到上限且未收到任何数据，可能是辅助流未启动或出错")
                    else:
                        logger.warning(f"[{req_id}] 流响应队列空读取次数达到上限 ({max_empty_retries})，结束读取")

                    # 返回超时完成信号，而不是简单退出
                    yield {"done": True, "reason": "internal_timeout", "body": "", "function": []}
                    return

                await asyncio.sleep(0.1)  # 100ms等待
                continue

    except Exception as e:
        logger.error(f"[{req_id}] 使用流响应时出错: {e}")
        raise
    finally:
        logger.info(f"[{req_id}] 流响应使用完成，数据接收状态: {data_received}")


async def clear_stream_queue():
    """清空流队列"""
    from server import STREAM_QUEUE, logger

    if STREAM_QUEUE is None:
        return

    try:
        # 清空队列中剩余的数据
        while True:
            try:
                STREAM_QUEUE.get_nowait()
            except:
                break
        logger.debug("流队列已清空")
    except Exception as e:
        logger.error(f"清空流队列时出错: {e}")


# --- Helper response generator ---
async def use_helper_get_response(helper_endpoint: str, helper_sapisid: str) -> AsyncGenerator[str, None]:
    """使用Helper服务获取响应的生成器"""
    from server import logger
    import aiohttp

    logger.info(f"正在尝试使用Helper端点: {helper_endpoint}")

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json',
                'Cookie': f'SAPISID={helper_sapisid}' if helper_sapisid else ''
            }

            async with session.get(helper_endpoint, headers=headers) as response:
                if response.status == 200:
                    async for chunk in response.content.iter_chunked(1024):
                        if chunk:
                            yield chunk.decode('utf-8', errors='ignore')
                else:
                    logger.error(f"Helper端点返回错误状态: {response.status}")

    except Exception as e:
        logger.error(f"使用Helper端点时出错: {e}")


# --- 请求验证函数 ---
def validate_chat_request(messages: List[Message], req_id: str) -> Dict[str, Optional[str]]:
    """验证聊天请求"""
    from server import logger

    if not messages:
        raise ValueError(f"[{req_id}] 无效请求: 'messages' 数组缺失或为空。")

    if not any(msg.role != 'system' for msg in messages):
        raise ValueError(f"[{req_id}] 无效请求: 所有消息都是系统消息。至少需要一条用户或助手消息。")

    # 返回验证结果
    return {
        "error": None,
        "warning": None
    }


# --- 提示准备函数 ---
def prepare_combined_prompt(messages: List[Message], req_id: str) -> str:
    """准备组合提示"""
    from server import logger

    logger.info(f"[{req_id}] (准备提示) 正在从 {len(messages)} 条消息准备组合提示 (包括历史)。")

    combined_parts = []
    system_prompt_content: Optional[str] = None
    processed_system_message_indices = set()

    # 处理系统消息
    for i, msg in enumerate(messages):
        if msg.role == 'system':
            content = msg.content
            if isinstance(content, str) and content.strip():
                system_prompt_content = content.strip()
                processed_system_message_indices.add(i)
                logger.info(f"[{req_id}] (准备提示) 在索引 {i} 找到并使用系统提示: '{system_prompt_content[:80]}...'")
                system_instr_prefix = "系统指令:\n"
                combined_parts.append(f"{system_instr_prefix}{system_prompt_content}")
            else:
                logger.info(f"[{req_id}] (准备提示) 在索引 {i} 忽略非字符串或空的系统消息。")
                processed_system_message_indices.add(i)
            break

    role_map_ui = {"user": "用户", "assistant": "助手", "system": "系统", "tool": "工具"}
    turn_separator = "\n---\n"

    # 处理其他消息
    for i, msg in enumerate(messages):
        if i in processed_system_message_indices:
            continue

        if msg.role == 'system':
            logger.info(f"[{req_id}] (准备提示) 跳过在索引 {i} 的后续系统消息。")
            continue

        if combined_parts:
            combined_parts.append(turn_separator)

        role = msg.role or 'unknown'
        role_prefix_ui = f"{role_map_ui.get(role, role.capitalize())}:\n"
        current_turn_parts = [role_prefix_ui]

        content = msg.content or ''
        content_str = ""

        if isinstance(content, str):
            content_str = content.strip()
        elif isinstance(content, list):
            # 处理多模态内容
            text_parts = []
            for item in content:
                if hasattr(item, 'type') and item.type == 'text':
                    text_parts.append(item.text or '')
                elif isinstance(item, dict) and item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                else:
                    logger.warning(f"[{req_id}] (准备提示) 警告: 在索引 {i} 的消息中忽略非文本或未知类型的 content item")
            content_str = "\n".join(text_parts).strip()
        else:
            logger.warning(f"[{req_id}] (准备提示) 警告: 角色 {role} 在索引 {i} 的内容类型意外 ({type(content)}) 或为 None。")
            content_str = str(content or "").strip()

        if content_str:
            current_turn_parts.append(content_str)

        # 处理工具调用
        tool_calls = msg.tool_calls
        if role == 'assistant' and tool_calls:
            if content_str:
                current_turn_parts.append("\n")

            tool_call_visualizations = []
            for tool_call in tool_calls:
                if hasattr(tool_call, 'type') and tool_call.type == 'function':
                    function_call = tool_call.function
                    func_name = function_call.name if function_call else None
                    func_args_str = function_call.arguments if function_call else None

                    try:
                        parsed_args = json.loads(func_args_str if func_args_str else '{}')
                        formatted_args = json.dumps(parsed_args, indent=2, ensure_ascii=False)
                    except (json.JSONDecodeError, TypeError):
                        formatted_args = func_args_str if func_args_str is not None else "{}"

                    tool_call_visualizations.append(
                        f"请求调用函数: {func_name}\n参数:\n{formatted_args}"
                    )

            if tool_call_visualizations:
                current_turn_parts.append("\n".join(tool_call_visualizations))

        if len(current_turn_parts) > 1 or (role == 'assistant' and tool_calls):
            combined_parts.append("".join(current_turn_parts))
        elif not combined_parts and not current_turn_parts:
            logger.info(f"[{req_id}] (准备提示) 跳过角色 {role} 在索引 {i} 的空消息 (且无工具调用)。")
        elif len(current_turn_parts) == 1 and not combined_parts:
            logger.info(f"[{req_id}] (准备提示) 跳过角色 {role} 在索引 {i} 的空消息 (只有前缀)。")

    final_prompt = "".join(combined_parts)
    if final_prompt:
        final_prompt += "\n"

    preview_text = final_prompt[:300].replace('\n', '\\n')
    logger.info(f"[{req_id}] (准备提示) 组合提示长度: {len(final_prompt)}。预览: '{preview_text}...'")

    return final_prompt


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in text
    Uses simple character counting method:
    - English: approximately 4 characters = 1 token
    - Chinese: approximately 1.5 characters = 1 token
    - Mixed text: uses weighted average
    """
    if not text:
        return 0

    # Count Chinese characters (including Chinese punctuation)
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff' or '\u3000' <= char <= '\u303f' or '\uff00' <= char <= '\uffef')

    # Count non-Chinese characters
    non_chinese_chars = len(text) - chinese_chars

    # Calculate token estimation
    chinese_tokens = chinese_chars / 1.5  # Chinese: approximately 1.5 chars/token
    english_tokens = non_chinese_chars / 4.0  # English: approximately 4 chars/token

    return max(1, int(chinese_tokens + english_tokens))


def calculate_usage_stats(messages: List[dict], response_content: str, reasoning_content: str = None) -> dict:
    """
    计算token使用统计

    Args:
        messages: 请求中的消息列表
        response_content: 响应内容
        reasoning_content: 推理内容（可选）

    Returns:
        包含token使用统计的字典
    """
    # 计算输入token（prompt tokens）
    prompt_text = ""
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        prompt_text += f"{role}: {content}\n"

    prompt_tokens = estimate_tokens(prompt_text)

    # 计算输出token（completion tokens）
    completion_text = response_content or ""
    if reasoning_content:
        completion_text += reasoning_content

    completion_tokens = estimate_tokens(completion_text)

    # 总token数
    total_tokens = prompt_tokens + completion_tokens

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens
    }


def generate_sse_stop_chunk_with_usage(req_id: str, model: str, usage_stats: dict, reason: str = "stop") -> str:
    """生成带usage统计的SSE停止块"""
    return generate_sse_stop_chunk(req_id, model, reason, usage_stats)
