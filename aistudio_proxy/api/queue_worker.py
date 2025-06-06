"""
队列工作器模块
处理请求队列中的任务
"""

import asyncio
import time
from fastapi import HTTPException


async def queue_worker():
    """队列工作器，处理请求队列中的任务"""
    # 导入全局变量
    from server import (
        logger, request_queue, processing_lock, model_switching_lock, 
        params_cache_lock
    )
    
    logger.info("--- 队列 Worker 已启动 ---")
    
    # 检查并初始化全局变量
    if request_queue is None:
        logger.info("初始化 request_queue...")
        from asyncio import Queue
        request_queue = Queue()
    
    if processing_lock is None:
        logger.info("初始化 processing_lock...")
        from asyncio import Lock
        processing_lock = Lock()
    
    if model_switching_lock is None:
        logger.info("初始化 model_switching_lock...")
        from asyncio import Lock
        model_switching_lock = Lock()
    
    if params_cache_lock is None:
        logger.info("初始化 params_cache_lock...")
        from asyncio import Lock
        params_cache_lock = Lock()
    
    was_last_request_streaming = False
    last_request_completion_time = 0
    
    while True:
        request_item = None
        result_future = None
        req_id = "UNKNOWN"
        completion_event = None
        
        try:
            # 检查队列中的项目，清理已断开连接的请求
            queue_size = request_queue.qsize()
            if queue_size > 0:
                checked_count = 0
                items_to_requeue = []
                processed_ids = set()
                
                while checked_count < queue_size and checked_count < 10:
                    try:
                        item = request_queue.get_nowait()
                        item_req_id = item.get("req_id", "unknown")
                        
                        if item_req_id in processed_ids:
                            items_to_requeue.append(item)
                            continue
                            
                        processed_ids.add(item_req_id)
                        
                        if not item.get("cancelled", False):
                            item_http_request = item.get("http_request")
                            if item_http_request:
                                try:
                                    if await item_http_request.is_disconnected():
                                        logger.info(f"[{item_req_id}] (Worker Queue Check) 检测到客户端已断开，标记为取消。")
                                        item["cancelled"] = True
                                        item_future = item.get("result_future")
                                        if item_future and not item_future.done():
                                            item_future.set_exception(HTTPException(status_code=499, detail=f"[{item_req_id}] Client disconnected while queued."))
                                except Exception as check_err:
                                    logger.error(f"[{item_req_id}] (Worker Queue Check) Error checking disconnect: {check_err}")
                        
                        items_to_requeue.append(item)
                        checked_count += 1
                    except asyncio.QueueEmpty:
                        break
                
                for item in items_to_requeue:
                    await request_queue.put(item)
            
            # 获取下一个请求
            try:
                request_item = await asyncio.wait_for(request_queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                # 如果5秒内没有新请求，继续循环检查
                continue
            
            req_id = request_item["req_id"]
            request_data = request_item["request_data"]
            http_request = request_item["http_request"]
            result_future = request_item["result_future"]
            
            if request_item.get("cancelled", False):
                logger.info(f"[{req_id}] (Worker) 请求已取消，跳过。")
                if not result_future.done():
                    result_future.set_exception(HTTPException(status_code=499, detail=f"[{req_id}] 请求已被用户取消"))
                request_queue.task_done()
                continue
            
            is_streaming_request = request_data.stream
            logger.info(f"[{req_id}] (Worker) 取出请求。模式: {'流式' if is_streaming_request else '非流式'}")
            
            # 流式请求间隔控制
            current_time = time.time()
            if was_last_request_streaming and is_streaming_request and (current_time - last_request_completion_time < 1.0):
                delay_time = max(0.5, 1.0 - (current_time - last_request_completion_time))
                logger.info(f"[{req_id}] (Worker) 连续流式请求，添加 {delay_time:.2f}s 延迟...")
                await asyncio.sleep(delay_time)
            
            if await http_request.is_disconnected():
                logger.info(f"[{req_id}] (Worker) 客户端在等待锁时断开。取消。")
                if not result_future.done():
                    result_future.set_exception(HTTPException(status_code=499, detail=f"[{req_id}] 客户端关闭了请求"))
                request_queue.task_done()
                continue
            
            logger.info(f"[{req_id}] (Worker) 等待处理锁...")
            async with processing_lock:
                logger.info(f"[{req_id}] (Worker) 已获取处理锁。开始核心处理...")
                
                if await http_request.is_disconnected():
                    logger.info(f"[{req_id}] (Worker) 客户端在获取锁后断开。取消。")
                    if not result_future.done():
                        result_future.set_exception(HTTPException(status_code=499, detail=f"[{req_id}] 客户端关闭了请求"))
                elif result_future.done():
                    logger.info(f"[{req_id}] (Worker) Future 在处理前已完成/取消。跳过。")
                else:
                    # 调用实际的请求处理函数
                    try:
                        from api_utils import _process_request_refactored
                        returned_value = await _process_request_refactored(
                            req_id, request_data, http_request, result_future
                        )
                        
                        if isinstance(returned_value, tuple) and len(returned_value) == 3:
                            completion_event, locator, checker = returned_value
                            if completion_event and locator and checker:
                                logger.info(f"[{req_id}] (Worker) _process_request_refactored returned stream info (event, locator, checker).")
                            else:
                                logger.info(f"[{req_id}] (Worker) _process_request_refactored returned a tuple, but completion_event is None (likely non-stream or early exit).")
                        elif returned_value is None:
                            logger.info(f"[{req_id}] (Worker) _process_request_refactored returned non-stream completion (None).")
                        else:
                            logger.warning(f"[{req_id}] (Worker) _process_request_refactored returned unexpected type: {type(returned_value)}")
                    except Exception as process_err:
                        logger.error(f"[{req_id}] (Worker) _process_request_refactored execution error: {process_err}")
                        if not result_future.done():
                            result_future.set_exception(HTTPException(status_code=500, detail=f"[{req_id}] Request processing error: {process_err}"))
            
            # 清空流式队列缓存
            logger.info(f"[{req_id}] (Worker) 尝试清空流式队列缓存...")
            from api_utils import clear_stream_queue
            await clear_stream_queue()
            logger.info(f"[{req_id}] (Worker) 释放处理锁。")
            
            was_last_request_streaming = is_streaming_request
            last_request_completion_time = time.time()
            
        except asyncio.CancelledError:
            logger.info("--- 队列 Worker 被取消 ---")
            if result_future and not result_future.done():
                result_future.cancel("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"[{req_id}] (Worker) ❌ 处理请求时发生意外错误: {e}", exc_info=True)
            if result_future and not result_future.done():
                result_future.set_exception(HTTPException(status_code=500, detail=f"[{req_id}] 服务器内部错误: {e}"))
        finally:
            if request_item:
                request_queue.task_done()
    
    logger.info("--- 队列 Worker 已停止 ---") 